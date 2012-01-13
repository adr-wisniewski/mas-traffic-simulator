/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.agent;

import jade.core.AID;
import jade.core.behaviours.Behaviour;
import jade.core.behaviours.FSMBehaviour;
import jade.core.behaviours.OneShotBehaviour;
import jade.core.behaviours.ReceiverBehaviour;
import jade.core.behaviours.ReceiverBehaviour.Handle;
import jade.core.behaviours.ReceiverBehaviour.NotYetReady;
import jade.core.behaviours.ReceiverBehaviour.TimedOut;
import jade.core.behaviours.SenderBehaviour;
import jade.core.behaviours.SequentialBehaviour;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import trafficsim.agent.EnvironmentMessage.RouteFinished;
import trafficsim.agent.JunctionMessage.DriveToRequest;

/**
 *
 * @author Adrian
 */
public class JunctionHandleVehicleBehaviour extends FSMBehaviour {

    private final Logger logger = Logger.getLogger(JunctionAgent.class.getName());
    
    private final static String STATE_INITIAL = "initial";
    private final static String STATE_VALIDATE = "validate";
    private final static String STATE_REQUEST_ENTER = "requesting-enter";
    private final static String STATE_REQUEST_LEAVE = "requesting-leave";
    private final static String STATE_REPLY_VEH = "reply";
    private final static String STATE_FINISH = "finish";
    
    private final static int RECEIVE_TIMEOUT_MS = 1000000;
    
    private final static int REQUEST_VALID = 0;
    private final static int REQUEST_INVALID = -1;

    private Handle receiverHandle = ReceiverBehaviour.newHandle();
    private JunctionAgent junctionAgent;
    private DriveToRequest request;
    private AID vehicle;
    private boolean requestValid;

    public JunctionHandleVehicleBehaviour(JunctionAgent a, DriveToRequest request, AID vehicle) {
        super(a); 
        this.junctionAgent = a;
        this.request = request;
        this.vehicle = vehicle;    
        setupStates();
    }

    private void setupStates() {
        registerTransition(STATE_INITIAL, STATE_REPLY_VEH, REQUEST_INVALID);
        registerDefaultTransition(STATE_INITIAL, STATE_VALIDATE);
        
        registerTransition(STATE_VALIDATE, STATE_REPLY_VEH, REQUEST_INVALID);
        registerDefaultTransition(STATE_VALIDATE, STATE_REQUEST_ENTER);
        
        registerTransition(STATE_REQUEST_ENTER, STATE_REPLY_VEH, REQUEST_INVALID);
        registerDefaultTransition(STATE_REQUEST_ENTER, STATE_REQUEST_LEAVE);
        
        registerDefaultTransition(STATE_REQUEST_LEAVE, STATE_REPLY_VEH);
        
        registerDefaultTransition(STATE_REPLY_VEH, STATE_FINISH);
        
        registerFirstState(createInitialBehaviour(), STATE_INITIAL);
        registerState(createValidateBehaviour(), STATE_VALIDATE);
        registerState(createRequestEnterBehaviour(), STATE_REQUEST_ENTER);
        registerState(createRequestLeaveBehaviour(), STATE_REQUEST_LEAVE);
        registerState(createReplyBehaviour(), STATE_REPLY_VEH);
        registerLastState(createFinishBehaviour(), STATE_FINISH);
    }

    private Behaviour createInitialBehaviour() {
        return new OneShotBehaviour() {
            @Override
            public void action() {
                logger.log(Level.INFO, "[{0}] INITIAL state start", new Object[]{junctionAgent.getName()});
                
                boolean alreadyServiced = junctionAgent.getVehicles().contains(vehicle) ;
                boolean invelidSource = request.getSource() != null && !junctionAgent.getIncomingEdges().contains(request.getSource());
                boolean invalidTarget = request.getDestination() != null && !junctionAgent.getOutgoingEdges().contains(request.getDestination());
                
                requestValid = !alreadyServiced && !invelidSource && !invalidTarget;
                logger.log(Level.INFO, "[{0}] INITIAL state finish {1} alreadyServiced:{2} invelidSource:{3} invalidTarget:{4}", 
                        new Object[]{junctionAgent.getName(), requestValid, invelidSource, invalidTarget});
            }

            @Override
            public int onEnd() {
                return requestValid ? REQUEST_VALID : REQUEST_INVALID;
            }
        };
    }
    
    private Behaviour createValidateBehaviour() {
        SequentialBehaviour b = new SequentialBehaviour(myAgent);
        
        if(request.getSource() != null) {
            try {
                AID sourceAgent = AgentUtil.getStreetAgent(request.getSource());
                
                ACLMessage message = new ACLMessage(ACLMessage.INFORM_IF);
                message.addReceiver(sourceAgent);
                message.setSender(myAgent.getAID());
                StreetMessage.IsVehicleAtEnd content = new StreetMessage.IsVehicleAtEnd(vehicle);
                message.setContentObject(content);
                
                MessageTemplate template = MessageTemplate.MatchSender(sourceAgent);
                
                b.addSubBehaviour(new SenderBehaviour(myAgent, message));
                b.addSubBehaviour(new ReceiverBehaviour(myAgent, receiverHandle, RECEIVE_TIMEOUT_MS, template));
            } catch (IOException ex) {
                Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        b.addSubBehaviour(new OneShotBehaviour() {   
            @Override
            public void action() {
                boolean result = false;
                
                logger.log(Level.INFO, "[{0}] VALIDATE source: {1}", new Object[]{junctionAgent.getName(), request.getSource()});
                if(request.getSource() == null) {
                    result = true;
                } else {
                    try {
                        ACLMessage message = receiverHandle.getMessage();
                        logger.log(Level.INFO, "[{0}] VALIDATE performative: {1}", new Object[]{junctionAgent.getName(), message.getPerformative() });
                        if(message.getPerformative() == ACLMessage.CONFIRM) {
                            result = true;
                        }
                    } catch (TimedOut ex) {
                        Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                    } catch (NotYetReady ex) {
                        Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                    }
                }
                
                requestValid = result;
                logger.log(Level.INFO, "[{0}] VALIDATE valid: {1}", new Object[]{junctionAgent.getName(), requestValid});
            }

            @Override
            public int onEnd() {
                return requestValid ? REQUEST_VALID : REQUEST_INVALID;
            }
        });
        return b;
    }
    
    private Behaviour createRequestEnterBehaviour() {
        SequentialBehaviour b = new SequentialBehaviour(myAgent);
        
        if(request.getDestination() != null) {
            try {
                AID destinationAgent = AgentUtil.getStreetAgent(request.getDestination());
                    
                ACLMessage message = new ACLMessage(ACLMessage.REQUEST);
                message.addReceiver(destinationAgent);
                message.setSender(myAgent.getAID());
                StreetMessage.VehicleEnter content = new StreetMessage.VehicleEnter(vehicle);
                message.setContentObject(content);

                MessageTemplate template = MessageTemplate.MatchSender(destinationAgent);

                b.addSubBehaviour(new SenderBehaviour(myAgent, message));
                b.addSubBehaviour(new ReceiverBehaviour(myAgent, receiverHandle, RECEIVE_TIMEOUT_MS, template));
            } catch (IOException ex) {
                Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        b.addSubBehaviour(new OneShotBehaviour() {
            
            boolean requestAccepted;
            
            @Override
            public void action() {

                boolean result = false;
                       
                logger.log(Level.INFO, "[{0}] ENTER destination:{1}", new Object[]{junctionAgent.getName(), request.getDestination()});
                if(request.getDestination() == null) {
                    result = true;
                } else {
                    try {
                        ACLMessage message = receiverHandle.getMessage();
                        logger.log(Level.INFO, "[{0}] ENTER performative:{1}", new Object[]{junctionAgent.getName(), message.getPerformative()});
                        if(message.getPerformative() == ACLMessage.AGREE) {
                            result = true;
                        }
                    } catch (TimedOut ex) {
                        Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                    } catch (NotYetReady ex) {
                        Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                    }
                }
                
                requestAccepted = result;
                logger.log(Level.INFO, "[{0}] ENTER valid:{1}", new Object[]{junctionAgent.getName(), requestAccepted});
            }

            @Override
            public int onEnd() {
                return requestAccepted ? REQUEST_VALID : REQUEST_VALID;
            }
        });
        
        return b;
        
    }
    
    private Behaviour createRequestLeaveBehaviour() {
        SequentialBehaviour b = new SequentialBehaviour(myAgent);
        
        if(request.getSource() != null) {
            try {
                AID sourceAgent = AgentUtil.getStreetAgent(request.getSource());
                    
                ACLMessage message = new ACLMessage(ACLMessage.REQUEST);
                message.addReceiver(sourceAgent);
                message.setSender(myAgent.getAID());
                StreetMessage.VehicleLeave content = new StreetMessage.VehicleLeave(vehicle);
                message.setContentObject(content);

                MessageTemplate template = MessageTemplate.MatchSender(sourceAgent);

                b.addSubBehaviour(new SenderBehaviour(myAgent, message));
                b.addSubBehaviour(new ReceiverBehaviour(myAgent, receiverHandle, RECEIVE_TIMEOUT_MS, template));
            } catch (IOException ex) {
                Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        b.addSubBehaviour(new OneShotBehaviour() {
            
            boolean requestAccepted;
            
            @Override
            public void action() {
                boolean result = false;
                                
                logger.log(Level.INFO, "[{0}] LEAVE source: {1}", new Object[]{junctionAgent.getName(), request.getSource()});
                if(request.getSource() == null) {
                    result = true;
                } else {
                    try {
                        ACLMessage message = receiverHandle.getMessage();
                        if(message != null && message.getPerformative() == ACLMessage.AGREE) {
                            result = true;
                        }
                    } catch (TimedOut ex) {
                        Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                    } catch (NotYetReady ex) {
                        Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                    }
                }
                
                requestAccepted = result;
                logger.log(Level.INFO, "[{0}] LEAVE valid: {1}", new Object[]{junctionAgent.getName(), requestAccepted});
            }

            @Override
            public int onEnd() {
                return requestAccepted ? REQUEST_VALID : REQUEST_VALID;
            }
        });
        
        return b;
    }
    
    private Behaviour createReplyBehaviour() {
        return new OneShotBehaviour() {
            @Override
            public void action() {
               try {
                    
                    if(!requestValid) {
                        request.setDestination(null);
                    }
                    
                    logger.log(Level.INFO, "[{0}] REPLY valid: {1} destination: {2}", new Object[]{junctionAgent.getName(), requestValid, request.getDestination()});
                    
                    ACLMessage message = new ACLMessage(ACLMessage.INFORM);
                    message.addReceiver(vehicle);
                    message.setSender(junctionAgent.getAID());
                    message.setContentObject(request);
                    junctionAgent.send(message);
                } catch (IOException ex) {
                    Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        };
    }

    private Behaviour createFinishBehaviour() {
        return new OneShotBehaviour() {
            @Override
            public void action() {
                logger.log(Level.INFO, "[{0}] FINISH destination: {1} final: {2} vertex: {3}", new Object[]{junctionAgent.getName(), request.getDestination(), request.getFinalDestination(), junctionAgent.getJunctionVertex()});
                    
                // vehile has finished it's route
                if(request.getDestination() == null) {
                    try {
                        logger.log(Level.INFO, "[{0}] FINISH vehicle:{1}", new Object[]{junctionAgent.getName(), vehicle.getLocalName()});
                
                        ACLMessage message = new ACLMessage(ACLMessage.INFORM);
                        message.addReceiver(AgentUtil.getEnvironmentAgent());
                        message.setSender(junctionAgent.getAID());
                        RouteFinished content = new RouteFinished();
                        content.setSucceeded(junctionAgent.getJunctionVertex().equals(request.getFinalDestination()));
                        content.setVehicle(vehicle);
                        message.setContentObject(content);
                        junctionAgent.send(message);
                    } catch (IOException ex) {
                        Logger.getLogger(JunctionHandleVehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                    }
                }

                boolean removed = junctionAgent.getVehicles().remove(vehicle);
                assert(removed);
            }
        };
    }
}
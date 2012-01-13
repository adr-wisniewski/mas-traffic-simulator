/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.agent;

import jade.core.AID;
import jade.core.behaviours.Behaviour;
import jade.core.behaviours.FSMBehaviour;
import jade.core.behaviours.OneShotBehaviour;
import jade.core.behaviours.SequentialBehaviour;
import jade.core.behaviours.SimpleBehaviour;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;
import jade.lang.acl.UnreadableException;
import jade.proto.states.MsgReceiver;
import java.io.IOException;
import java.io.Serializable;
import java.util.logging.Level;
import java.util.logging.Logger;
import trafficsim.agent.JunctionMessage.DriveToRequest;
import trafficsim.agent.StreetMessage.ConditionInfo;
import trafficsim.data.JunctionVertex;
import trafficsim.data.StreetEdge;

/**
 *
 * @author Adrian
 */
public class VehicleBehaviour extends FSMBehaviour {

    private final Logger logger = Logger.getLogger(VehicleBehaviour.class.getName());
    
    private static final String STATE_INITIAL = "initial";
    private static final String STATE_STREET = "on-street";
    private static final String STATE_JUNCTION = "on-junction";
    private static final String STATE_TERMINATE = "terminate";
    
    private static final int ROUTE_FINISHED = 1;
    private static final int ROUTE_NOTFINISHED = 0;
    
    private VehicleAgent vehicleAgent;
    private AID currentJunctionAgent;
    private AID currentStreetAgent;
    private MsgReceiver msgReceiver;
    
    private JunctionVertex currentJunction;
    private StreetEdge currentStreet;
    private JunctionVertex destination;
    

    public VehicleBehaviour(VehicleAgent v) {
        super(v);
        this.vehicleAgent = v;
        
        registerDefaultTransition(STATE_INITIAL, STATE_JUNCTION);
        registerTransition(STATE_JUNCTION, STATE_TERMINATE, ROUTE_FINISHED);
        registerDefaultTransition(STATE_JUNCTION, STATE_STREET, new String[]{STATE_STREET});
        registerDefaultTransition(STATE_STREET, STATE_JUNCTION, new String[]{STATE_JUNCTION});

        Behaviour initial = createInitialBehaviour();
        registerFirstState(initial, STATE_INITIAL);
        
        Behaviour junction = createJunctionBehaviour();
        registerState(junction, STATE_JUNCTION);
        
        Behaviour driving = createStreetBehaviour();
        registerState(driving, STATE_STREET);

        Behaviour terminate = createTerminateBehaviour();
        registerLastState(terminate, STATE_TERMINATE);
    }

    private Behaviour createInitialBehaviour() {
        return new OneShotBehaviour(myAgent) {
            @Override
            public void action() {
                logger.log(Level.INFO, "[{0}] INITIAL", new Object[]{vehicleAgent.getName()});
                currentStreet = null;
                currentStreetAgent = null;
                currentJunction = vehicleAgent.getNavigator().getStartPoint();
                currentJunctionAgent = AgentUtil.getJunctionAgent(currentJunction);
                destination = vehicleAgent.getNavigator().getEndPoint();
            }
        };
    }
    
    private Behaviour createJunctionBehaviour() {
        SequentialBehaviour b = new SequentialBehaviour(myAgent) {
            @Override
            public int onEnd() {
                return currentStreet != null && currentStreetAgent != null ? ROUTE_NOTFINISHED : ROUTE_FINISHED;
            }
        };
        
        b.addSubBehaviour(new OneShotBehaviour(myAgent) {
            @Override
            public void action() {
                
                try {
                    StreetEdge proposedDestionation = vehicleAgent.getNavigator().getNextStreet(currentJunction);
                    
                    // send terminated message and delete self
                    ACLMessage message = new ACLMessage(ACLMessage.REQUEST);
                    message.addReceiver(currentJunctionAgent);
                    message.setSender(myAgent.getAID());
                    DriveToRequest driveToRequest = new DriveToRequest();
                    driveToRequest.setDestination(proposedDestionation);
                    driveToRequest.setFinalDestination(destination);
                    driveToRequest.setSource(currentStreet);
                    message.setContentObject(driveToRequest);
                    myAgent.send(message);        
                    msgReceiver.setTemplate(MessageTemplate.MatchSender(currentJunctionAgent));
                    
                    logger.log(Level.INFO, "[{0}] JUNCTION SEND request:{1} to:{2}", new Object[]{vehicleAgent.getName(), driveToRequest.toString(), currentJunctionAgent.getLocalName()});
                } catch (IOException ex) {
                    Logger.getLogger(VehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                    throw new RuntimeException(ex);
                }
            }
        });
        
        msgReceiver = new MsgReceiver(myAgent, null, MsgReceiver.INFINITE, getDataStore(), myAgent);
        b.addSubBehaviour(msgReceiver);
        
        b.addSubBehaviour(new OneShotBehaviour(myAgent) {
            @Override
            public void action() { 
                logger.log(Level.INFO, "[{0}] JUNCTION RECEIVE", new Object[]{vehicleAgent.getName()});
                currentStreet = null;
                currentStreetAgent = null;
                ACLMessage message = (ACLMessage)VehicleBehaviour.this.getDataStore().get(myAgent);
                if(message != null) {
                    try {
                        DriveToRequest reply = (DriveToRequest)message.getContentObject();
                        currentStreet = reply.getDestination();
                        currentStreetAgent = (currentStreet == null ? null : AgentUtil.getStreetAgent(currentStreet));
                        logger.log(Level.INFO, "[{0}] JUNCTION RECEIVE reply:{1}", new Object[]{vehicleAgent.getName(), reply.toString()});
                    } catch (UnreadableException ex) {
                        Logger.getLogger(VehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                    }
                }
            }
        });

        return b;
    }
    
    private Behaviour createStreetBehaviour() {
        return new SimpleBehaviour(myAgent) {
            private boolean finished = false;
            @Override
            public void action() {
                logger.log(Level.INFO, "[{0}] STREET currentStreetAgent:{1}", new Object[]{vehicleAgent.getName(), currentStreetAgent.getLocalName()});
                finished = false;
                ACLMessage message = myAgent.receive(MessageTemplate.MatchSender(currentStreetAgent));
                if(message != null) {
                    try {
                        Serializable contentObject = message.getContentObject();
                        if(contentObject instanceof StreetMessage.ConditionInfo) {
                            ConditionInfo conditionInfo = (ConditionInfo) contentObject;
                            logger.log(Level.INFO, "[{0}] STREET Received message ConditionInfo: {1} from {2}", new Object[]{myAgent.getName(), conditionInfo.toString(), message.getSender().getLocalName() });
                            handleConditionInfo(conditionInfo);
                        }
                    } catch (UnreadableException ex) {
                        Logger.getLogger(VehicleBehaviour.class.getName()).log(Level.SEVERE, null, ex);
                    }
                } else {
                    block();
                }
            }

            @Override
            public boolean done() {
                return finished;
            }

            private void handleConditionInfo(ConditionInfo conditionInfo) {
                if (conditionInfo.getObstacleDistanceM() < 0.1 && conditionInfo.getJunction() != null) {
                    currentJunction = conditionInfo.getJunction();
                    currentJunctionAgent = AgentUtil.getJunctionAgent(currentJunction);
                    finished = true;
                }
            }
        };
    }

    private Behaviour createTerminateBehaviour() {
        Behaviour b = new OneShotBehaviour(myAgent) {
            @Override
            public void action() {
                logger.log(Level.INFO, "[{0}] TERMINATE", new Object[]{vehicleAgent.getName()});
                myAgent.doDelete();
            }
        };
        return b;
    }
}

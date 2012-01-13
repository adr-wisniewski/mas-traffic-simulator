/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.agent;

import jade.core.AID;
import jade.core.Agent;
import jade.core.behaviours.CyclicBehaviour;
import jade.core.behaviours.TickerBehaviour;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.UnreadableException;
import java.io.IOException;
import java.io.Serializable;
import java.util.LinkedList;
import java.util.logging.Level;
import java.util.logging.Logger;
import trafficsim.agent.EnvironmentMessage.VehicleUpdated;
import trafficsim.agent.StreetMessage.IsVehicleAtEnd;
import trafficsim.agent.StreetMessage.VehicleEnter;
import trafficsim.agent.StreetMessage.VehicleLeave;
import trafficsim.data.JunctionVertex;
import trafficsim.data.MetricsUtil;
import trafficsim.data.StreetEdge;

/**
 *
 * @author Adrian
 */
public class StreetAgent extends Agent {

    private static final long UPDATE_INTERVAL_MS = 10;
    private static final long ENVIRONMENT_INFO_INTERVAL_MS = 50;
    private static final long INFO_INTERVAL_SIM_S = 1;
    private static final double VEHICLE_MAX_SPEED_KMPH = 50;
    private static final double VEHICLE_FRONT_SPACE_M = 5;
    
    private LinkedList<VehicleInfo> waitingQueue = new LinkedList<VehicleInfo>();
    private LinkedList<VehicleInfo> vehicles = new LinkedList<VehicleInfo>();
    private double streetLengthM;
    private StreetEdge streetEdge;
    private JunctionVertex endJunction;
    private long lastUpdateTimeMs;
    
    @Override
    protected void setup() {
        super.setup();
        Object[] arguments = getArguments();
        
        streetEdge = (StreetEdge)arguments[0];
        endJunction = (JunctionVertex)arguments[1];
        streetLengthM = ((Double)arguments[2]).doubleValue();
        lastUpdateTimeMs = System.currentTimeMillis();
        
        long agentInfoTickTimeMs = (long)MetricsUtil.sToMs(MetricsUtil.toRealTime(INFO_INTERVAL_SIM_S));
        assert(agentInfoTickTimeMs > 0);
        addBehaviour(new StreetUpdateBehaviour(this, UPDATE_INTERVAL_MS));
        addBehaviour(new AgentInfoSenderBehaviour(this, agentInfoTickTimeMs));
        addBehaviour(new EnvironmentInfoSenderBehaviour(this, ENVIRONMENT_INFO_INTERVAL_MS));
        addBehaviour(new StreetRequestResponderBehaviour());
    }
    
    protected boolean queueVehicle(AID vehicle, AID owner) {
        if(!hasVehicle(vehicle)) {
            waitingQueue.addLast(new VehicleInfo(vehicle, owner));
            return true;
        }
        
        return false;
    }
    
    protected boolean letVehicleIn(AID vehicle) {
        if(!hasVehicle(vehicle)) {
            vehicles.addLast(new VehicleInfo(vehicle));
            return true;
        }
        
        return false;
    }
    
    private boolean letVehicleOut(AID vehicle) {
        if(isVehicleAtEnd(vehicle)) {
            vehicles.removeFirst();
            return true;
        }
        
        return false;
    }
    
    private boolean isVehicleAtEnd(AID vehicle) {
        VehicleInfo first = vehicles.getFirst();
        
        if(first != null && first.vehicle.equals(vehicle) && first.positionM == streetLengthM) {
            return true;
        }
        
        return false;
    }
    
    private boolean hasVehicle(AID sender) {
        for(VehicleInfo info: vehicles) {
            if(info.vehicle.equals(sender)) {
                return true;
            }
        }
        
        return false;
    }
    
    private boolean hasSpaceForVehicle() {
        return vehicles.isEmpty() || vehicles.getLast().positionM > VEHICLE_FRONT_SPACE_M;
    }

    private void updateVehicles() {
        
        double elapsedSimulationTimeH = getElapsedSimulationTimeH();
        
        // update positions
        VehicleInfo prev = null;
        for(VehicleInfo info: vehicles) {
            double maxPositionM = prev == null ? streetLengthM : prev.getPositionM() - VEHICLE_FRONT_SPACE_M;
            info.positionM += MetricsUtil.kmToM(elapsedSimulationTimeH * VEHICLE_MAX_SPEED_KMPH);
            info.positionM = Math.min(info.positionM, maxPositionM);
            prev = info;
        }
        
        // update waiting queue
        if(!waitingQueue.isEmpty() && hasSpaceForVehicle()) {
            VehicleInfo first = waitingQueue.getFirst();
            waitingQueue.removeFirst();
            
            boolean result = letVehicleIn(first.vehicle);
            assert(result);
            
            reply(result ? ACLMessage.AGREE : ACLMessage.REFUSE, first.getOwner());
        }
    }
    
    private void sendAgentInfo() {
        VehicleInfo prev = null;
        for(VehicleInfo info: vehicles) {
            try {
                StreetMessage.ConditionInfo conditions = new StreetMessage.ConditionInfo();
                
                if(prev == null) {
                    conditions.setObstacleDistanceM(streetLengthM - info.positionM);
                    conditions.setJunction(endJunction);
                } else {
                    conditions.setObstacleDistanceM(prev.positionM - info.positionM);
                    conditions.setVehicle(prev.vehicle);
                }
                
                ACLMessage message = new ACLMessage(ACLMessage.INFORM);
                message.addReceiver(info.getVehicle());
                message.setSender(getAID());
                message.setContentObject(conditions);
                send(message);

                prev = info;
            } catch (IOException ex) {
                Logger.getLogger(StreetAgent.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }
    
    private void sendEnvironmentInfo() {
        for(VehicleInfo info: vehicles) {
            try {
                VehicleUpdated update = new EnvironmentMessage.VehicleUpdated(streetEdge, info.positionM, info.vehicle.getLocalName());
                ACLMessage message = new ACLMessage(ACLMessage.INFORM);
                message.addReceiver(AgentUtil.getEnvironmentAgent());
                message.setSender(getAID());
                message.setContentObject(update);
                send(message);
            } catch (IOException ex) {
                Logger.getLogger(StreetAgent.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }

    private double getElapsedSimulationTimeH() {
        long currentTimeMs = System.currentTimeMillis();
        long elapsedTimeMs = currentTimeMs - lastUpdateTimeMs;
        lastUpdateTimeMs = currentTimeMs;
        return MetricsUtil.toSimulationTime(MetricsUtil.msToH(elapsedTimeMs));
    }

    private void handleVehicleEnter(VehicleEnter vehicleEnter, AID sender) {
        assert(!hasVehicle(vehicleEnter.getVehicle()));
        boolean result = queueVehicle(vehicleEnter.getVehicle(), sender);
        assert(result);
        
        // refuse if queueing failed
        if(!result) {
            reply(ACLMessage.REFUSE, sender);
        }
    }
    
    private void handleVehicleLeave(VehicleLeave vehicleLeave, AID sender) {
        assert(hasVehicle(vehicleLeave.getVehicle()));
        boolean result = letVehicleOut(vehicleLeave.getVehicle());
        assert(result);
        reply(result ? ACLMessage.AGREE : ACLMessage.REFUSE, sender);
    }
    
    private void handleIsVehicleAtEnd(IsVehicleAtEnd vehicleAtEnd, AID sender) {
        assert(hasVehicle(vehicleAtEnd.getVehicle()));
        boolean result = isVehicleAtEnd(vehicleAtEnd.getVehicle());
        reply(result ? ACLMessage.CONFIRM : ACLMessage.DISCONFIRM, sender);
    }

    private void reply(int performative, AID sender) {
        ACLMessage message = new ACLMessage(performative);
        message.addReceiver(sender);
        message.setSender(getAID());
        send(message);
    }

    private class StreetUpdateBehaviour extends TickerBehaviour {

        public StreetUpdateBehaviour(Agent a, long period) {
            super(a, period);
        }

        @Override
        protected void onTick() {
            updateVehicles();
        }
    
    }
    
    private class AgentInfoSenderBehaviour extends TickerBehaviour {

        public AgentInfoSenderBehaviour(Agent a, long period) {
            super(a, period);
        }
        
        @Override
        protected void onTick() {
            sendAgentInfo();
        }
    }
    
    private class EnvironmentInfoSenderBehaviour extends TickerBehaviour {

        public EnvironmentInfoSenderBehaviour(Agent a, long period) {
            super(a, period);
        }

        @Override
        protected void onTick() {
            sendEnvironmentInfo();
        }
    }
    
    private class StreetRequestResponderBehaviour extends CyclicBehaviour {

        @Override
        public void action() {
            ACLMessage msg = myAgent.receive();
            if (msg != null) {
                try {
                    Serializable contentObject = msg.getContentObject();
                    AID sender = msg.getSender();
                    
                    if(contentObject instanceof StreetMessage.VehicleEnter) {
                        StreetMessage.VehicleEnter vehicleEnter = (StreetMessage.VehicleEnter) contentObject;
                        Logger.getLogger(StreetAgent.class.getName()).log(Level.INFO, "[{0}] Received message StreetMessage.VehicleEnter: {1} from {2}", new Object[]{myAgent.getName(), vehicleEnter.toString(), sender.getLocalName()});
                        handleVehicleEnter(vehicleEnter, sender);
                    } else if(contentObject instanceof StreetMessage.VehicleLeave) {
                        StreetMessage.VehicleLeave vehicleLeave = (StreetMessage.VehicleLeave) contentObject;
                        Logger.getLogger(StreetAgent.class.getName()).log(Level.INFO, "[{0}] Received message StreetMessage.VehicleLeave: {1} from {2}", new Object[]{myAgent.getName(), vehicleLeave.toString(), sender.getLocalName()});
                        handleVehicleLeave(vehicleLeave, sender);
                    } if(contentObject instanceof StreetMessage.IsVehicleAtEnd) {
                        StreetMessage.IsVehicleAtEnd isVehicleAtEnd = (StreetMessage.IsVehicleAtEnd) contentObject;
                        Logger.getLogger(StreetAgent.class.getName()).log(Level.INFO, "[{0}] Received message StreetMessage.IsVehicleAtEnd: {1} from {2}", new Object[]{myAgent.getName(), isVehicleAtEnd.toString(), sender.getLocalName()});
                        handleIsVehicleAtEnd(isVehicleAtEnd, sender);
                    } 
                } catch (UnreadableException ex) {
                    Logger.getLogger(StreetAgent.class.getName()).log(Level.SEVERE, "[{0}] msg:{1}", new Object[]{getName(), msg.toString()});
                    Logger.getLogger(StreetAgent.class.getName()).log(Level.SEVERE, null, ex);
                }
            } else {
                block();
            }
        }
    }
    
    private class VehicleInfo {
        private AID vehicle;
        private AID owner;
        private double positionM;

        public VehicleInfo(AID vehicle) {
            this.vehicle = vehicle;
            this.positionM = 0;
        }

        public VehicleInfo(AID vehicle, AID owner) {
            this(vehicle);
            this.owner = owner;
        }

        public AID getVehicle() {
            return vehicle;
        }

        public void setVehicle(AID vehicle) {
            this.vehicle = vehicle;
        }

        public double getPositionM() {
            return positionM;
        }

        public void setPositionM(double position) {
            this.positionM = position;
        }

        /**
         * @return the owner
         */
        public AID getOwner() {
            return owner;
        }
    }
}

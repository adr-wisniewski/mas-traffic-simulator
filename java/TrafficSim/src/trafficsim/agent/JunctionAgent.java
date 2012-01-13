/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.agent;

import jade.core.AID;
import jade.core.Agent;
import jade.core.behaviours.Behaviour;
import jade.core.behaviours.CyclicBehaviour;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;
import jade.lang.acl.UnreadableException;
import java.io.Serializable;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;
import trafficsim.agent.JunctionMessage.DriveToRequest;
import trafficsim.data.JunctionVertex;
import trafficsim.data.StreetEdge;

/**
 *
 * @author Adrian
 */
public class JunctionAgent extends Agent {
    //private final static long TICK_INTERVAL_MS = 10;
    
    //private JunctionStrategyFactory strategyFactory = new JunctionStrategyFactory();
    //private JunctionStrategy strategy;
    private JunctionVertex vertex;
    private Set<StreetEdge> incomingEdges;
    private Set<StreetEdge> outgoingEdges;
    private List<AID> vehicles = new LinkedList<AID>();

    @Override
    protected void setup() {
        Object[] arguments = getArguments();
        
        assert(arguments.length == 3);
        vertex = (JunctionVertex) arguments[0];
        incomingEdges = (Set<StreetEdge>) arguments[1];
        outgoingEdges = (Set<StreetEdge>) arguments[2];
        //strategy = strategyFactory.getStrategy( vertex.getStrategyClass());
        
        Behaviour b = createRequestResponderBehaviour();
        addBehaviour(b); 
    }

    private Behaviour createRequestResponderBehaviour() {
        return new CyclicBehaviour(this) {
            @Override
            public void action() {
                try {
                    ACLMessage message = myAgent.receive(MessageTemplate.MatchPerformative(ACLMessage.REQUEST));
                    if(message != null) {    
                        Serializable contentObject = message.getContentObject();
                        if( contentObject != null && contentObject instanceof DriveToRequest) {
                            DriveToRequest request = (DriveToRequest)contentObject;
                            AID vehicle = message.getSender();
                            Logger.getLogger(JunctionAgent.class.getName()).log(Level.INFO, "[{0}] received message: {1} from {2}", new Object[]{getName(), request.toString(), vehicle.getLocalName()});
                            handleRequest(request, vehicle);
                        }    
                    } else {
                        block();
                    }
                } catch (UnreadableException ex) {
                    Logger.getLogger(JunctionAgent.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        };
    }
    
    private void handleRequest(DriveToRequest request, AID vehicle) {
        Logger.getLogger(JunctionAgent.class.getName()).log(Level.INFO, "[{0}] adding handler for vehicle {1}", new Object[]{getName(), vehicle.getLocalName()});
        addBehaviour(new JunctionHandleVehicleBehaviour(this, request, vehicle));
    }

    /**
     * @return the vertex
     */
    public JunctionVertex getJunctionVertex() {
        return vertex;
    }

    /**
     * @return the vehicles
     */
    public List<AID> getVehicles() {
        return vehicles;
    }

    /**
     * @return the incomingEdges
     */
    public Set<StreetEdge> getIncomingEdges() {
        return incomingEdges;
    }

    /**
     * @return the outgoingEdges
     */
    public Set<StreetEdge> getOutgoingEdges() {
        return outgoingEdges;
    }
}

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.agent;

import jade.core.AID;
import jade.core.behaviours.CyclicBehaviour;
import jade.gui.GuiAgent;
import jade.gui.GuiEvent;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.UnreadableException;
import jade.wrapper.AgentContainer;
import jade.wrapper.AgentController;
import jade.wrapper.ControllerException;
import java.io.Serializable;
import java.util.HashSet;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;
import trafficsim.agent.EnvironmentMessage.RouteFinished;
import trafficsim.agent.EnvironmentMessage.VehicleUpdated;
import trafficsim.data.JunctionVertex;
import trafficsim.data.StreetEdge;
import trafficsim.model.EnvironmentModel;

/**
 *
 * @author Adrian
 */
public class EnvironmentAgent extends GuiAgent {
    // agent references
    private Set<AID> vehicleAgents = new HashSet<AID>();
    private Set<AID> streetAgents = new HashSet<AID>();
    private Set<AID> junctionAgents = new HashSet<AID>();
    
    // model
    private EnvironmentModel model;
    private int vehicleCount;
    
    @Override
    protected void setup() {
        CreateModel();
        CreateGraphAgents();
        CreateVehicles();
        model.StartSimulation();
        
        addBehaviour(new ListenerBehaviour());
    }
    
    private void CreateModel() {
        Object[] args = getArguments();
        
        if(args.length != 2) {
            throw new IllegalArgumentException("Excepted 2 arguments");
        }

        String graphGeneratorName = (String)args[0];
        vehicleCount = Integer.parseInt((String)args[1]);
        if(vehicleCount <= 0) {
            throw new IllegalArgumentException("Excepted positive vehicle count");
        }
        
        model = new EnvironmentModel(graphGeneratorName);
    }
    
    private void CreateGraphAgents() {
        AgentContainer container = getContainerController();

        try {
            Set<StreetEdge> edgeSet = model.getGraph().edgeSet();
            for(StreetEdge edge: edgeSet) {
                double streetLengthM = model.getGraph().getEdgeWeight(edge);
                JunctionVertex junction = model.getGraph().getEdgeTarget(edge);
                Object[] args = new Object[] {edge, junction, streetLengthM};
                String name = AgentUtil.getStreetAgentName(edge);
                
                AgentController a = container.createNewAgent(name, StreetAgent.class.getCanonicalName(), args );
                a.start();

                streetAgents.add(AgentUtil.getStreetAgent(edge));
            }
            
            Set<JunctionVertex> vertexSet = model.getGraph().vertexSet();
            for(JunctionVertex vertex: vertexSet) {
                String name = AgentUtil.getJunctionAgentName(vertex);
                Set<StreetEdge> incomingEdges = model.getGraph().incomingEdgesOf(vertex);
                Set<StreetEdge> outgoingEdges = model.getGraph().outgoingEdgesOf(vertex);
                Object[] args = new Object[] {vertex, incomingEdges, outgoingEdges};
                AgentController a = container.createNewAgent(name, JunctionAgent.class.getCanonicalName(), args );
                a.start();
                
                junctionAgents.add(AgentUtil.getJunctionAgent(vertex));
            }
            
        } catch (ControllerException ex) {
            throw new RuntimeException(ex);
        }
    }
    
    private void CreateVehicles() {
        AgentContainer container = getContainerController();
        
        try {
            for(int ordinal = 0; ordinal < vehicleCount; ++ordinal) {
                String name = AgentUtil.getVehicleAgentName(ordinal);
                Object[] args = new Object[] {model.getGraph().clone()};
                AgentController a = container.createNewAgent(name, VehicleAgent.class.getCanonicalName(), args );
                a.start();   
                
                vehicleAgents.add(AgentUtil.getVehicleAgent(ordinal));
                model.onVehicleCreated(name);
            }
        }
        catch (ControllerException ex) {
            throw new RuntimeException(ex);
        }
    }
    
    @Override
    protected void onGuiEvent(GuiEvent ev) {
        throw new UnsupportedOperationException("Not supported yet.");
    }
    
    private class ListenerBehaviour extends CyclicBehaviour {

        @Override
        public void action() {
            ACLMessage msg = myAgent.receive();
            if (msg != null) {
                try {
                    Serializable contentObject = msg.getContentObject();
                    AID sender = msg.getSender();
                    
                    if(contentObject instanceof RouteFinished) {
                        RouteFinished routeFinished = (RouteFinished) contentObject;
                        Logger.getLogger(StreetAgent.class.getName()).log(Level.INFO, "[{0}] Received message RouteFinished: {1} from {2}", new Object[]{myAgent.getName(), routeFinished.toString(), sender.getLocalName()});
                        model.onVehicleTerminated(routeFinished.getVehicle().getLocalName(), routeFinished.isSucceeded());
                    } else if (contentObject instanceof VehicleUpdated) {
                        VehicleUpdated vehicleUpdated = (VehicleUpdated) contentObject;
                        //Logger.getLogger(StreetAgent.class.getName()).log(Level.INFO, "[{0}] Received message VehicleUpdated: {1} from {2}", new Object[]{myAgent.getName(), vehicleUpdated.toString(), sender.getLocalName()});
                        model.onVehicleUpdated(vehicleUpdated);
                    }
                } catch (UnreadableException ex) {
                    Logger.getLogger(EnvironmentAgent.class.getName()).log(Level.SEVERE, null, ex);
                }
            } else {
                block();
            }
        }
    }
}

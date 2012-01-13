/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.model;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import trafficsim.agent.EnvironmentMessage.VehicleUpdated;
import trafficsim.data.StreetGraph;
import trafficsim.data.StreetGraphFactory;
import trafficsim.ui.MainFrame;

/**
 *
 * @author Adrian
 */
public class EnvironmentModel {
    private List<VehicleEventListener> vehicleEventListeners = new LinkedList<VehicleEventListener>();
    
    // graph stuff
    private Map<String, VehicleState> approximateVehicleState = new HashMap<String, VehicleState>();
    private final StreetGraphFactory graphFactory = new StreetGraphFactory();
    private StreetGraph graph;
    
    // gui stuff
    private MainFrame mainFrame;
    
     // simulation statistics
    private boolean simulationFinished = false;
    private long simulationStartTimeMs = 0;
    private long simulationEndTimeMs = 0;
    private int totalVehicleCount = 0;
    private int vehicleCount = 0;

    public EnvironmentModel(String graphGeneratorName) {
        this.graph = graphFactory.getGraph(graphGeneratorName);
        this.mainFrame = new MainFrame(this);
        this.mainFrame.setTitle("Environment Model");
        mainFrame.setVisible(true);
    }
    
    public void StartSimulation() {
        simulationStartTimeMs = System.currentTimeMillis();
    }
    
    /**
     * @return the graph
     */
    public StreetGraph getGraph() {
        return graph;
    }

    /**
     * @return the vehicleCount
     */
    public int getVehicleCount() {
        return vehicleCount;
    }
    
    public long getSimulationTime() {
        return simulationEndTimeMs == 0 ? 
                System.currentTimeMillis() - simulationStartTimeMs : 
                simulationEndTimeMs - simulationStartTimeMs;
    }

    /**
     * @return the initialVehicleCount
     */
    public int getTotalVehicleCount() {
        return totalVehicleCount;
    }

    public void onVehicleCreated(String vehicleName) {
        assert(!simulationFinished);
        VehicleState vehicleState = new VehicleState(vehicleName);
        approximateVehicleState.put(vehicleName, vehicleState);
        ++totalVehicleCount;
        ++vehicleCount;
        fireVehicleEvent(VehicleEventType.CREATED, vehicleState);
    }
    
    public void onVehicleUpdated(VehicleUpdated updateMessage) {
        assert(!simulationFinished);
        VehicleState state = approximateVehicleState.get(updateMessage.getVehicleName());
        
        assert(state != null);
        if(state != null) {
            double totalDitance = graph.getEdgeWeight(updateMessage.getStreet());
            state.setStreet(updateMessage.getStreet());
            state.setStreetDistanceM(updateMessage.getDistanceM());
            state.setStreetDistanceFactor(updateMessage.getDistanceM()/totalDitance);
            fireVehicleEvent(VehicleEventType.UPDATED, state);
        }
    }
    
    public void onVehicleTerminated(String vehicleName, boolean succeeded) {
        assert(!simulationFinished);
        
        VehicleState state = approximateVehicleState.get(vehicleName);
        assert(state != null);
        if(state != null) {
            state.setTerminated(true);
            state.setStreet(null);
            state.setStreetDistanceM(0);
            state.setStreetDistanceFactor(0);
            state.setSucceeded(succeeded);
            fireVehicleEvent(VehicleEventType.UPDATED, state);
        }
        
        assert(vehicleCount > 0);
        --vehicleCount;
        if(vehicleCount == 0) {
            finishSimulation();
        }
    }

    private void finishSimulation() {
        assert(vehicleCount == 0);
        assert(!simulationFinished);
        
        simulationFinished = true;
        simulationEndTimeMs = System.currentTimeMillis();
        
        mainFrame.ShowEndSimulationMessage();
    }

    public boolean isSimulationFinished() {
        return simulationFinished;
    }

    /**
     * @return the approximateVehicleState
     */
    public Map<String, VehicleState> getApproximateVehicleState() {
        return approximateVehicleState;
    }
    
    public void addVehicleEventListener(VehicleEventListener listener) {
        vehicleEventListeners.add(listener);
    }
    
    private void fireVehicleEvent(VehicleEventType vehicleEventType, VehicleState state) {
        for(VehicleEventListener listener : vehicleEventListeners) {
            listener.onVehicleEvent(vehicleEventType, state);
        }
    }
}

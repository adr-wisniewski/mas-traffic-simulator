/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.agent;


import jade.core.AID;
import jade.core.Agent;
import trafficsim.data.StreetGraph;
import trafficsim.model.VehicleNavigator;


/**
 *
 * @author Adrian
 */
public class VehicleAgent extends Agent {

    private VehicleNavigator navigator;
    private AID environmentAgent;

    @Override
    protected void setup() {
        super.setup();
        
        Object[] arguments = getArguments();
        StreetGraph graph = (StreetGraph)arguments[0];
        
        navigator = new VehicleNavigator(this, graph);
        environmentAgent = AgentUtil.getEnvironmentAgent();
        
        addBehaviour(new VehicleBehaviour(this));
    }

    /**
     * @return the navigator
     */
    protected VehicleNavigator getNavigator() {
        return navigator;
    }
}

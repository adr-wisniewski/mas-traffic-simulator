/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.agent;

import jade.core.AID;
import jade.core.Agent;
import trafficsim.data.JunctionVertex;
import trafficsim.data.StreetEdge;

/**
 *
 * @author Adrian
 */
public final class AgentUtil {
    private AgentUtil() {
        // prevent instantiation
    }
    
    static final private String ENVIRONMENT_AGENT_NAME = "env";
    static final private String VEHICLE_AGENT_NAME_FORMAT = "Vehicle %d";
    static final private String STREET_AGENT_NAME_FORMAT = "Street %s";
    static final private String JUNCTION_AGENT_NAME_FORMAT = "Junction %s";
    
    public static AID getEnvironmentAgent() {
        return new AID(ENVIRONMENT_AGENT_NAME, AID.ISLOCALNAME);
    }
    
    public static AID getStreetAgent(StreetEdge street){
        return new AID(getStreetAgentName(street), AID.ISLOCALNAME);
    }
    
    public static AID getJunctionAgent(JunctionVertex junction){
        return new AID(getJunctionAgentName(junction), AID.ISLOCALNAME);
    }
    
    public static AID getVehicleAgent(int ordinal){
        return new AID(getVehicleAgentName(ordinal), AID.ISLOCALNAME);
    } 
    
    public static String getEnvironmentAgentName() {
        return ENVIRONMENT_AGENT_NAME;
    }
    
    public static String getStreetAgentName(StreetEdge street) {
        return String.format(STREET_AGENT_NAME_FORMAT, street.getName());
    }
    
    public static String getJunctionAgentName(JunctionVertex junction) {
        return String.format(JUNCTION_AGENT_NAME_FORMAT, junction.getName());
    }
    
    public static String getVehicleAgentName(int ordinal) {
        return String.format(VEHICLE_AGENT_NAME_FORMAT, ordinal);
    }
    
    public static String createConvId(Agent agent) {
        // as in jade.proto.Initiator
        String convId = "C"+agent.hashCode()+"_"+System.currentTimeMillis()+"_";
        return convId;
    }
}

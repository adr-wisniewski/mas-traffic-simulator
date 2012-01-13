/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.model;

import java.util.List;
import java.util.Random;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.jgrapht.alg.DijkstraShortestPath;
import trafficsim.agent.VehicleAgent;
import trafficsim.data.JunctionVertex;
import trafficsim.data.StreetEdge;
import trafficsim.data.StreetGraph;

/**
 *
 * @author Adrian
 */

public class VehicleNavigator {
        
    private VehicleAgent agent;
    private StreetGraph graph;
    private JunctionVertex startPoint;
    private JunctionVertex endPoint;
    List<StreetEdge> path;

    public VehicleNavigator(VehicleAgent agent, StreetGraph graph) {
        this.agent = agent;
        this.graph = graph;
        
        pickStartAndEndPoint();
        findPath();
    }

    private void pickStartAndEndPoint() {
        Set<JunctionVertex> vertexSet = graph.vertexSet();
        int vertices = vertexSet.size();
        JunctionVertex[] array = vertexSet.toArray(new JunctionVertex[vertices]); // TODO: performance

        Random random = new Random();
        startPoint = array[random.nextInt(vertices)];

        do {
            endPoint = array[random.nextInt(vertices)];
        } while(startPoint == endPoint);
        
        Logger.getLogger(VehicleNavigator.class.getName()).log(Level.INFO, "[{0}] Route from {1} to {2}", new Object[]{agent.getName(), startPoint.getName(), endPoint.getName()});
    }

    private void findPath() {
        path = DijkstraShortestPath.findPathBetween(graph, startPoint, endPoint); 

        if(path == null) {
            Logger.getLogger(VehicleNavigator.class.getName()).log(Level.SEVERE, "[{0}] Path is null!", agent.getName());
        } else if(path.isEmpty()) {
            Logger.getLogger(VehicleNavigator.class.getName()).log(Level.WARNING, "[{0}] Couldn't find path", agent.getName());
        }
    }
    
    public JunctionVertex getStartPoint() {
        return startPoint;
    }
    
    public JunctionVertex getEndPoint() {
        return endPoint;
    }
    
    public boolean isDestinationReachable() {
        return path == null;
    }
    
    public StreetEdge getNextStreet(JunctionVertex junction) {
        if(path != null) {
            for(StreetEdge street: path) {
                JunctionVertex edgeSource = graph.getEdgeSource(street);
                if(edgeSource.equals(junction)) {
                    return street;
                }

            }
        }
        
        return null;
    }
}

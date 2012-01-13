/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.data;

import org.jgrapht.graph.SimpleDirectedWeightedGraph;

/**
 *
 * @author Adrian
 */
public class StreetGraph extends SimpleDirectedWeightedGraph<JunctionVertex, StreetEdge> {

    public StreetGraph() {
        super(StreetEdge.class);
    }

    @Override
    public void setEdgeWeight(StreetEdge e, double weight) {
        throw new UnsupportedOperationException();
    }

    @Override
    public double getEdgeWeight(StreetEdge e) {
        JunctionVertex edgeSource = getEdgeSource(e);
        JunctionVertex edgeTarget = getEdgeTarget(e);
        return edgeSource.getDistanceTo(edgeTarget);
    }
}

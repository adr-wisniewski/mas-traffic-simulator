/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.data.generator;

import trafficsim.data.JunctionVertex;
import trafficsim.data.StreetEdge;
import trafficsim.data.StreetGraph;
import trafficsim.data.StreetGraphGenerator;

/**
 *
 * @author Adrian
 */
public class SimpleStreetGraphGenerator implements StreetGraphGenerator {

    @Override
    public StreetGraph Generate() {
        StreetGraph g = new StreetGraph();
        
        JunctionVertex v0 = new JunctionVertex("v0", +000, +000);
        JunctionVertex v1 = new JunctionVertex("vBL", -50, -50);
        JunctionVertex v2 = new JunctionVertex("vTR", +50, +50);
        JunctionVertex v3 = new JunctionVertex("vBR", +50, -50);
        JunctionVertex v4 = new JunctionVertex("vTL", -50, +50);
        JunctionVertex v5 = new JunctionVertex("v5", -100, -100);
        JunctionVertex v6 = new JunctionVertex("v6", +100, +100);
        JunctionVertex v7 = new JunctionVertex("v7", +100, -100);
        JunctionVertex v8 = new JunctionVertex("v8", -100, +100);
        
        g.addVertex(v0);
        g.addVertex(v1);
        g.addVertex(v2);
        g.addVertex(v3);
        g.addVertex(v4);
        g.addVertex(v5);
        g.addVertex(v6);
        g.addVertex(v7);
        g.addVertex(v8);
        
        g.addEdge(v0, v1, new StreetEdge("0-1"));
        g.addEdge(v0, v2, new StreetEdge("0-2"));
        g.addEdge(v0, v3, new StreetEdge("0-3"));
        g.addEdge(v0, v4, new StreetEdge("0-4"));
        
        g.addEdge(v1, v0, new StreetEdge("1-0"));
        g.addEdge(v1, v3, new StreetEdge("1-3 B"));
        g.addEdge(v1, v4, new StreetEdge("1-4 L"));
        
        g.addEdge(v2, v0, new StreetEdge("2-0"));
        g.addEdge(v2, v3, new StreetEdge("2-3 R"));
        g.addEdge(v2, v4, new StreetEdge("2-4 T"));
        
        g.addEdge(v3, v1, new StreetEdge("3-1 B"));
        g.addEdge(v3, v2, new StreetEdge("3-2 R"));
        g.addEdge(v3, v0, new StreetEdge("3-0"));
        
        g.addEdge(v4, v1, new StreetEdge("4-1 L"));
        g.addEdge(v4, v2, new StreetEdge("4-2 T"));
        g.addEdge(v4, v0, new StreetEdge("4-0"));
        
        g.addEdge(v1, v5, new StreetEdge("1-5"));
        g.addEdge(v5, v1, new StreetEdge("5-1"));
        
        g.addEdge(v2, v6, new StreetEdge("2-6"));
        g.addEdge(v6, v2, new StreetEdge("6-2"));
        
        g.addEdge(v3, v7, new StreetEdge("3-7"));
        g.addEdge(v7, v3, new StreetEdge("7-3"));
        
        g.addEdge(v4, v8, new StreetEdge("4-8"));
        g.addEdge(v8, v4, new StreetEdge("8-4"));
        
        return g;
    }
    
}

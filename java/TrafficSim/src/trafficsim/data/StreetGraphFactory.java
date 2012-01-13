/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.data;

import java.util.HashMap;
import java.util.Map;
import trafficsim.data.generator.SimpleStreetGraphGenerator;

/**
 *
 * @author Adrian
 */
public class StreetGraphFactory {
    
    static final Map<String, StreetGraphGenerator> generators = new HashMap<String, StreetGraphGenerator>();

    static {
        generators.put("simple", new SimpleStreetGraphGenerator());
   
        // TODO: add some generators here
    }
    
    public StreetGraph getGraph(String name) {
        StreetGraphGenerator generator = generators.get(name);
        
        if(generator == null) {
            throw new IllegalArgumentException();
        }
        
        return generator.Generate();
    }
}

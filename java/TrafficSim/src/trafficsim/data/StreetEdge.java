/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.data;

import java.io.Serializable;
import org.jgrapht.graph.DefaultEdge;

/**
 *
 * @author Adrian
 */
public class StreetEdge extends DefaultEdge implements Serializable {
    private String name;

    public StreetEdge(String name) {
        this.name = name;
    }

    /**
     * @return the name
     */
    public String getName() {
        return name;
    }

    /**
     * @param name the name to set
     */
    public void setName(String name) {
        this.name = name;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final StreetEdge other = (StreetEdge) obj;
        if ((this.name == null) ? (other.name != null) : !this.name.equals(other.name)) {
            return false;
        }
        return true;
    }

    @Override
    public int hashCode() {
        int hash = 3;
        hash = 17 * hash + (this.name != null ? this.name.hashCode() : 0);
        return hash;
    }

    @Override
    public String toString() {
        return super.toString() + " name: " + name;
    }

}

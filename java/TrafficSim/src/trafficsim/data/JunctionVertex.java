/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.data;

import java.awt.geom.Point2D;
import java.io.Serializable;

/**
 *
 * @author Adrian
 */
public class JunctionVertex implements Serializable {
    private String name;
    private Point2D pointM;

    public JunctionVertex(String name, double xM, double yM) {
        this.name = name;
        this.pointM = new Point2D.Double(xM,yM);
    }
    
    public double getDistanceTo(JunctionVertex destination) {
        return pointM.distance(destination.getPointM());
    }
    
    /**
     * @return the name
     */
    public String getName() {
        return name;
    }

    /**
     * @return the point
     */
    public Point2D getPointM() {
        return pointM;
    }

    @Override
    public String toString() {
        return super.toString() + " name: " + name;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final JunctionVertex other = (JunctionVertex) obj;
        if ((this.name == null) ? (other.name != null) : !this.name.equals(other.name)) {
            return false;
        }
        if (this.pointM != other.pointM && (this.pointM == null || !this.pointM.equals(other.pointM))) {
            return false;
        }
        return true;
    }

    @Override
    public int hashCode() {
        int hash = 7;
        hash = 97 * hash + (this.name != null ? this.name.hashCode() : 0);
        hash = 97 * hash + (this.pointM != null ? this.pointM.hashCode() : 0);
        return hash;
    }
}

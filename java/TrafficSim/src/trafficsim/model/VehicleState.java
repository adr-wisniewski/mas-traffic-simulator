/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.model;

import java.util.logging.Level;
import java.util.logging.Logger;
import trafficsim.data.StreetEdge;

/**
 *
 * @author Adrian
 */
public class VehicleState implements Cloneable {
    private String name;
    private StreetEdge street;
    private double streetDistanceM;
    private boolean terminated = false;
    private double streetDistanceFactor;
    private boolean succeeded = false;

    public VehicleState(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public StreetEdge getStreet() {
        return street;
    }


    public void setStreet(StreetEdge street) {
        this.street = street;
    }

    public double getStreetDistanceM() {
        return streetDistanceM;
    }

    public void setStreetDistanceM(double streetDistanceM) {
        this.streetDistanceM = streetDistanceM;
    }

    public boolean isTerminated() {
        return terminated;
    }

    public void setTerminated(boolean terminated) {
        this.terminated = terminated;
    }

    @Override
    public VehicleState clone() {
        try {
            return (VehicleState)super.clone();
        } catch (CloneNotSupportedException ex) {
            Logger.getLogger(VehicleState.class.getName()).log(Level.SEVERE, null, ex);
            throw new RuntimeException(ex);
        }
    }

    void setStreetDistanceFactor(double streetDistanceFactor) {
        this.streetDistanceFactor = streetDistanceFactor;
    }

    /**
     * @return the distanceFactor
     */
    public double getStreetDistanceFactor() {
        return streetDistanceFactor;
    }

    /**
     * @return the succeeded
     */
    public boolean isSucceeded() {
        return succeeded;
    }

    /**
     * @param succeeded the succeeded to set
     */
    public void setSucceeded(boolean succeeded) {
        this.succeeded = succeeded;
    }
}

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.model;


/**
 *
 * @author Adrian
 */
public interface VehicleEventListener {
    public void onVehicleEvent(VehicleEventType type, VehicleState state);
}



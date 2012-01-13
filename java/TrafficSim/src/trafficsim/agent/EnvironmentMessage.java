/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.agent;

import jade.core.AID;
import java.io.Serializable;
import trafficsim.data.StreetEdge;

/**
 *
 * @author Adrian
 */
public interface EnvironmentMessage extends Serializable {
    
    public static class VehicleUpdated implements StreetMessage {

        private StreetEdge street;
        private double distanceM;
        private String vehicleName;

        public VehicleUpdated(StreetEdge street, double distanceM, String vehicleName) {
            this.street = street;
            this.distanceM = distanceM;
            this.vehicleName = vehicleName;
        }

        /**
         * @return the street
         */
        public StreetEdge getStreet() {
            return street;
        }

        /**
         * @return the distanceM
         */
        public double getDistanceM() {
            return distanceM;
        }

        /**
         * @return the vehicleNam
         */
        public String getVehicleName() {
            return vehicleName;
        }

        @Override
        public String toString() {
            return super.toString() 
                    + " street: " + street.getName()
                    + " distanceM: " + distanceM
                    + " vehicleName: " + vehicleName;
        }
    }
    
    public static class RouteFinished implements EnvironmentMessage {
        private boolean succeeded;
        private AID vehicle;

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

        void setVehicle(AID vehicle) {
            this.vehicle = vehicle;
        }

        @Override
        public String toString() {
            return super.toString() 
                    + " vehicle: " + getVehicle().getLocalName()
                    + " succeeded: " + succeeded;
        }

        /**
         * @return the vehicle
         */
        public AID getVehicle() {
            return vehicle;
        }
        
        
    }
}

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.agent;

import jade.core.AID;
import java.io.Serializable;
import trafficsim.data.JunctionVertex;

/**
 *
 * @author Adrian
 */
public interface StreetMessage extends Serializable {

    public static class VehicleEnter implements StreetMessage {
        private AID vehicle;

        public VehicleEnter(AID vehicle) {
            this.vehicle = vehicle;
        }

        /**
         * @return the vehicle
         */
        public AID getVehicle() {
            return vehicle;
        }

        @Override
        public String toString() {
            return super.toString() + " vehicle: " + vehicle.getLocalName();
        }
    }
    
    public static class VehicleLeave implements StreetMessage {
        private AID vehicle;

        public VehicleLeave(AID vehicle) {
            this.vehicle = vehicle;
        }

        /**
         * @return the vehicle
         */
        public AID getVehicle() {
            return vehicle;
        }
        
        @Override
        public String toString() {
            return super.toString() + " vehicle: " + vehicle.getLocalName();
        }
    }
    
    public static class IsVehicleAtEnd implements StreetMessage {
        private AID vehicle;

        public IsVehicleAtEnd(AID vehicle) {
            this.vehicle = vehicle;
        }

        /**
         * @return the vehicle
         */
        public AID getVehicle() {
            return vehicle;
        }
        
        @Override
        public String toString() {
            return super.toString() + " vehicle: " + vehicle.getLocalName();
        }
    }
    
    public static class ConditionInfo implements StreetMessage {
        private double obstacleDistanceM;
        private JunctionVertex junction;
        private AID vehicle;

        /**
         * @return the distance
         */
        public double getObstacleDistanceM() {
            return obstacleDistanceM;
        }

        /**
         * @param distance the distance to set
         */
        public void setObstacleDistanceM(double obstacleDistanceM) {
            this.obstacleDistanceM = obstacleDistanceM;
        }

        /**
         * @return the junction
         */
        public JunctionVertex getJunction() {
            return junction;
        }

        /**
         * @param junction the junction to set
         */
        public void setJunction(JunctionVertex junction) {
            this.junction = junction;
        }

        void setVehicle(AID vehicle) {
            this.vehicle = vehicle;
        }

        /**
         * @return the vehicle
         */
        public AID getVehicle() {
            return vehicle;
        }
        
        @Override
        public String toString() {
            return super.toString() 
                    + " obstacleDistanceM: " + obstacleDistanceM
                    + " junction: " + (junction != null ? junction.getName() : "<null>")
                    + " vehicle: " + (vehicle != null ? vehicle.getLocalName() : "<null>");
        }
    }
  
}

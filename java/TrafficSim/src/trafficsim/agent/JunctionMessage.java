/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.agent;

import java.io.Serializable;
import java.util.logging.Level;
import java.util.logging.Logger;
import trafficsim.data.JunctionVertex;
import trafficsim.data.StreetEdge;

/**
 *
 * @author Adrian
 */
public interface JunctionMessage extends Serializable {
    public static class DriveToRequest implements JunctionMessage, Cloneable {

        private JunctionVertex finalDestination;
        private StreetEdge destination;
        private StreetEdge source;
        
        void setDestination(StreetEdge destination) {
            this.destination = destination;
        }

        void setSource(StreetEdge source) {
            this.source = source;
        }

        /**
         * @return the destination
         */
        public StreetEdge getDestination() {
            return destination;
        }

        /**
         * @return the source
         */
        public StreetEdge getSource() {
            return source;
        }

        void setFinalDestination(JunctionVertex finalDestination) {
            this.finalDestination = finalDestination;
        }

        /**
         * @return the finalDestination
         */
        public JunctionVertex getFinalDestination() {
            return finalDestination;
        }

        @Override
        public String toString() {
            return super.toString() 
                    + " destination: " + (destination != null ? destination.getName() : "<null>")
                    + " source: " + (source != null ? source.getName() : "<null>")
                    + " finalDestination: " + (finalDestination != null ? finalDestination.getName() : "<null>");
        }
    }
}

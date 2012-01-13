/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.data;

/**
 *
 * @author Adrian
 */
public final class MetricsUtil {

    private MetricsUtil() {
        // prevent instantiation
    }
    
    // conversion is 1 real second = 1 simulation second * multiplier
    // simulation time is deliberatly so slow, because otherwise it would be 
    // hard to track vehicle's behaviour (it could go from start to end in few seconds)
    private static final double SIMULATION_TIME_MULTIPLIER = 1.0;
    private static final double TIME_MS_TO_SIMULATION = 1.0 * SIMULATION_TIME_MULTIPLIER;
    
    public static double toSimulationTime(double realTime) {
        return realTime * TIME_MS_TO_SIMULATION;
    }
    
    public static double toRealTime(double simTime) {
        return simTime / TIME_MS_TO_SIMULATION;
    }
    
    // This methods were introduced to quickly find all places
    // where conversions are made. It is useful to track down potential errors.
    public static double msToH(double ms) {
        return ms / ( 1000 * 60 * 60 );
    }
    
    public static double hToMs(double ms) {
        return ms * ( 1000 * 60 * 60 );
    }
    
    public static double msToS(double ms) {
        return ms /  1000;
    }
    
    public static double sToMs(double ms) {
        return ms * 1000;
    }
    
    public static double kmToM(double i) {
        return i * 1000.0;
    }
    
    public static double mToKm(double i) {
        return i / 1000.0;
    }
}

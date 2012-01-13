/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/*
 * Map.java
 *
 * Created on 2012-01-02, 20:02:30
 */
package trafficsim.ui;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.Stroke;
import java.awt.geom.Point2D;
import java.util.Set;
import trafficsim.data.JunctionVertex;
import trafficsim.data.StreetEdge;
import trafficsim.data.StreetGraph;
import trafficsim.model.EnvironmentModel;
import trafficsim.model.VehicleState;

/**
 *
 * @author Adrian
 */
public class MapPanel extends javax.swing.JPanel {

    // statics
    private static final double M_TO_PIXEL = 1.0;
    private static final int JUNCTION_RADIUS = 9;
    private static final int VEHICLE_RADIUS = 5;
    private static final Stroke streetStroke = new BasicStroke(2.0f);
    
    // colors
    private static final Color VehicleColor1 = Color.WHITE;
    private static final Color VehicleColor2 = Color.RED;
    private static final Color StreetColor = new Color(153,153,255);
    private static final Color JunctionColor = new Color(153,153,255);
    
    // membres
    private EnvironmentModel model;

    /** Creates new form Map */
    public MapPanel() {
        initComponents();
    }
    
    private int mToPixel(double positionM) {
        return (int)(positionM * M_TO_PIXEL);
    }
    
    private double pixelToM(int positionPx) {
        return (int)(positionPx / M_TO_PIXEL);
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        setBackground(new java.awt.Color(0, 0, 0));
        setBorder(javax.swing.BorderFactory.createEtchedBorder());
        setMinimumSize(new java.awt.Dimension(100, 100));
        setOpaque(false);

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 596, Short.MAX_VALUE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 596, Short.MAX_VALUE)
        );
    }// </editor-fold>//GEN-END:initComponents
    // Variables declaration - do not modify//GEN-BEGIN:variables
    // End of variables declaration//GEN-END:variables

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
    }
    
    @Override
    public void paint(Graphics g) {
        super.paint(g);
        
        g.setColor(Color.BLACK);
        g.fillRect(0, 0, getWidth(),getHeight());
        
        Graphics2D g2 = (Graphics2D)g;
        
        if(getModel() == null) {
            return;
        }
        
        StreetGraph graph = model.getGraph();
        Dimension size = getSize();
        g2.translate(size.width / 2, size.height / 2);
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        
        // streets
        Set<StreetEdge> edgeSet = graph.edgeSet();
        g.setColor(StreetColor);
        for(StreetEdge edge: edgeSet) {
            JunctionVertex edgeSource = graph.getEdgeSource(edge);
            JunctionVertex edgeTarget = graph.getEdgeTarget(edge);
            g2.setStroke(streetStroke);
            Point2D from = edgeSource.getPointM();
            Point2D to = edgeTarget.getPointM();
            g2.drawLine(mToPixel(from.getX()), mToPixel(from.getY()), mToPixel(to.getX()), mToPixel(to.getY()));
        }
        
        // junctions
        Set<JunctionVertex> vertexSet = graph.vertexSet();
        g.setColor(JunctionColor);
        for(JunctionVertex vertex: vertexSet) {
            Point2D point = vertex.getPointM();
            g2.fillOval(mToPixel(point.getX()) - JUNCTION_RADIUS/2, mToPixel(point.getY()) - JUNCTION_RADIUS/2, JUNCTION_RADIUS, JUNCTION_RADIUS);
        }
        
        // vehicles (paint non terminated, deployed on street)
        for(VehicleState vehicle: model.getApproximateVehicleState().values()) {
            if(!vehicle.isTerminated() && vehicle.getStreet() != null) {
                StreetEdge street = vehicle.getStreet();
                Point2D source = graph.getEdgeSource(street).getPointM();
                Point2D target = graph.getEdgeTarget(street).getPointM();
                double totalDistance = graph.getEdgeWeight(street);
                double distanceFraction = vehicle.getStreetDistanceM() / totalDistance;
                assert(distanceFraction >= 0.0 && distanceFraction <= 1.0);

                double dx = target.getX() - source.getX();
                double dy = target.getY() - source.getY();
                double length = Math.sqrt(dx*dx + dy*dy);
                
                dx = dx/length;
                dy = dy/length;
                
                double junctionInM = pixelToM(JUNCTION_RADIUS);
                double reducedLengthPx = Math.max(0, length - junctionInM);
                
                double xM = source.getX() + dx * (junctionInM/2 + reducedLengthPx * distanceFraction);
                double yM = source.getY() + dy * (junctionInM/2 + reducedLengthPx * distanceFraction);

                double dir = Math.abs(dy) > 0.2 ? dy : dx;
                
                g.setColor(dir > 0 ? VehicleColor1 : VehicleColor2);
                g2.fillOval(mToPixel(xM) - VEHICLE_RADIUS/2, mToPixel(yM) - VEHICLE_RADIUS/2, VEHICLE_RADIUS, VEHICLE_RADIUS);
            }
        }
    }

    /**
     * @return the model
     */
    public EnvironmentModel getModel() {
        return model;
    }

    /**
     * @param model the model to set
     */
    public void setModel(EnvironmentModel model) {
        this.model = model;
    }
}

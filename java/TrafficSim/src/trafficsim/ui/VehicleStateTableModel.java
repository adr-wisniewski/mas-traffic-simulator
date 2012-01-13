/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package trafficsim.ui;

import java.util.ArrayList;
import javax.swing.table.AbstractTableModel;
import trafficsim.model.VehicleState;

/**
 *
 * @author Adrian
 */
public class VehicleStateTableModel extends AbstractTableModel {

    private String[] columnNames = new String[]{"Vehicle", "State", "Street", "Distance", "Factor"};
    private ArrayList<VehicleState> data = new ArrayList<VehicleState>();
    
    @Override
    public String getColumnName(int col) {
        return columnNames[col].toString();
    }
   
    @Override
    public boolean isCellEditable(int row, int col) { 
        return false; 
    }
    
    @Override
    public int getRowCount() {
        return data.size();
    }

    @Override
    public int getColumnCount() {
        return columnNames.length;
    }

    @Override
    public Object getValueAt(int rowIndex, int columnIndex) {
        VehicleState row = data.get(rowIndex);
        
        switch(columnIndex) {
            case 0: return row.getName();
            case 1: return row.isTerminated() ? (row.isSucceeded() ? "Succeeded" : "Failed" ) : "Running";
            case 2: return row.getStreet() != null ? row.getStreet().getName() : "<null>";
            case 3: return row.getStreetDistanceM();
            case 4: return row.getStreetDistanceFactor();
            default: return null;
        }
    }

    void UpdateData(VehicleState stateCopy) {
        
        for(int i = 0, s = data.size(); i < s; ++i) {
            VehicleState row = data.get(i);
            
            if(row.getName().equals(stateCopy.getName())) {
                data.set(i, stateCopy);
                fireTableRowsUpdated(i, i);
                return;
            }
        }
       
        data.add(stateCopy);
        int rowOrdinal = data.size() - 1;
        fireTableRowsInserted(rowOrdinal, rowOrdinal);
    }
    
}

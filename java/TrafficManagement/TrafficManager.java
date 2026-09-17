package TrafficManagement;

import java.util.ArrayList;
import java.util.List;

class Road {
    private String roadName;
    private int vehicleCount;
    private String congestionLevel;

    public Road(String name, int count, String level) {
        this.roadName = name;
        this.vehicleCount = count;
        this.congestionLevel = level;
    }

    public String getCongestionLevel() { return congestionLevel; }
    
    @Override
    public String toString() {
        return roadName + " | Vehicles: " + vehicleCount + " | Level: " + congestionLevel;
    }
}

public class TrafficManager {
    public static void main(String[] args) {
        List<Road> roads = new ArrayList<>();
        roads.add(new Road("Main Expressway", 3200, "SEVERE"));
        roads.add(new Road("Airport Road", 800, "LOW"));

        System.out.println("--- Traffic Management System (Java Component) ---");
        for(Road r : roads) {
            System.out.println(r);
        }
    }
}

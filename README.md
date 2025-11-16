# FSAE Suspension Geometry Viewer

This application visualizes FSAE suspension geometry using data from an Excel file.

## Project Structure

The application has been restructured into a modular architecture:

```
FSAE_VD/
├── main.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── app.py             # Main application class
│   ├── data_loader.py     # Data loading utilities
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── geometry_tab.py        # Geometry visualization tab
│   │   ├── kinematics_tab.py      # Kinematics analysis tab
│   │   ├── analysis_tab.py        # General analysis tab
│   │   ├── tire_analysis_tab.py   # Tire model analysis tab
│   │   └── load_conditions_tab.py # Load conditions analysis tab
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── plotting.py            # 3D plotting utilities
│   │   └── tables.py              # Interactive table utilities
│   └── calculations/
│       ├── __init__.py
│       ├── tire_model.py          # Tire model implementation
│       ├── force_calculator.py    # Suspension force calculations
│       └── motion_ratio_calculator.py # Motion ratio calculations
└── README.md
```

## Running the Application

Run the main entry point:

```bash
python main.py
```

## Features

- **Geometry Tab**: 3D visualization of suspension points and connections
- **Kinematics Tab**: Analysis tools for suspension kinematics
- **Analysis Tab**: General analysis features
- **Tire Analysis Tab**: Tire model analysis using Pacejka model for FSAE TTC data
- **Load Conditions Tab**: Suspension load analysis under various external forces
- Interactive tables for editing suspension coordinates
- Multiple view controls (Top, Side, Isometric)

## Dependencies

- pandas
- numpy
- matplotlib
- tkinter
- openpyxl (for Excel reading)

## Data Source

The application loads suspension data from `Geo.xlsx` located at:
`C:\Users\charl\OneDrive - Tennessee Tech University\Fall 2025\FSAE\Geo.xlsx`

Update the path in `src/data_loader.py` if needed.
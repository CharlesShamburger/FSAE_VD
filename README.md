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
│   │   ├── geometry_tab.py    # Geometry visualization tab
│   │   ├── kinematics_tab.py  # Kinematics analysis tab
│   │   └── analysis_tab.py    # Analysis tab (placeholder)
│   └── utils/
│       ├── __init__.py
│       ├── plotting.py        # 3D plotting utilities
│       └── tables.py          # Interactive table utilities
├── Motion_Ratio.py         # Motion ratio calculation script
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
- **Analysis Tab**: Placeholder for future analysis features
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
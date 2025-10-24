# Development Guide

## Project Structure

```
crowd-management-system/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── setup.py               # Package setup
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Git ignore rules
├── core/                  # Core logic modules
│   ├── __init__.py        # Package initializer
│   └── detection.py       # Computer vision and detection logic
├── templates/             # HTML templates
│   ├── __init__.py        # Package initializer
│   └── index.html         # Main interface template
├── static/                # Static assets
│   ├── __init__.py        # Package initializer
│   ├── css/               # Stylesheets
│   │   ├── __init__.py    # Package initializer
│   │   └── style.css      # Main stylesheet
│   ├── js/                # JavaScript files
│   │   ├── __init__.py    # Package initializer
│   │   └── main.js        # Frontend logic
│   └── images/            # Image assets
│       ├── __init__.py    # Package initializer
├── components/            # Reusable UI components
│   └── __init__.py        # Package initializer
├── docs/                  # Documentation
│   ├── architecture.md    # System architecture
│   ├── user_guide.md      # User guide
│   └── development.md     # Development guide
├── tests/                 # Unit tests (to be implemented)
└── yolov3.cfg             # YOLOv3 configuration
```

## Setting Up Development Environment

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/crowd-management-system.git
   cd crowd-management-system
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download YOLOv3 weights:**
   - Download `yolov3.weights` from [YOLO website](https://pjreddie.com/darknet/yolo/)
   - Place the file in the project root directory

## Code Organization

### Core Module (`core/detection.py`)

The core detection module handles all computer vision logic:

- **CrowdDetector Class**: Main class for crowd detection
- **Model Initialization**: Loads YOLOv3 and Haar Cascade models
- **Database Operations**: SQLite database interactions
- **Detection Logic**: Real-time people counting and face detection

### Web Application (`app.py`)

The Flask web application provides the user interface:

- **Flask Routes**: API endpoints for frontend interactions
- **Camera Management**: Thread-safe camera operations
- **Real-time Streaming**: Video feed streaming to browser
- **Statistics Updates**: Real-time data updates

### Frontend (`templates/` and `static/`)

The frontend provides a modern web interface:

- **HTML Templates**: Jinja2 templates for dynamic content
- **CSS Styling**: Responsive design with dark theme
- **JavaScript Logic**: Client-side interactions and updates

## Development Workflow

### Adding New Features

1. **Branch Creation:**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Implementation:**
   - Follow existing code patterns and conventions
   - Add appropriate error handling
   - Include docstrings for new functions and classes
   - Write unit tests for new functionality

3. **Testing:**
   - Run existing tests to ensure no regressions
   - Test new functionality manually
   - Verify cross-browser compatibility

4. **Documentation:**
   - Update README.md if necessary
   - Add docstrings to new functions
   - Update user guide for user-facing features

5. **Commit and Push:**
   ```bash
   git add .
   git commit -m "Add new feature description"
   git push origin feature/new-feature-name
   ```

### Code Style Guidelines

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Include type hints where appropriate
- Write comprehensive docstrings
- Keep functions small and focused
- Use consistent indentation (4 spaces)

### Testing

Currently, the project includes a basic test script (`test_detection.py`). Future development should include:

- Unit tests for core detection logic
- Integration tests for web API endpoints
- UI tests for frontend functionality
- Performance tests for real-time processing

## Extending Functionality

### Adding New Detection Models

To add support for different object detection models:

1. Create a new model loader in `core/detection.py`
2. Update the detection logic to support the new model
3. Add configuration options in `config.py`
4. Update the web interface to display new information

### Adding New Alert Types

To add new alert types:

1. Update the alert level calculation in `app.py`
2. Add new CSS classes for visual styling
3. Update the JavaScript to handle new alert levels
4. Modify the threshold configuration in `config.py`

### Adding Database Fields

To add new fields to the database:

1. Update the database schema in `core/detection.py`
2. Modify the data insertion logic
3. Update any database query functions
4. Ensure backward compatibility

## Performance Considerations

### Optimization Tips

- Use efficient NumPy operations where possible
- Minimize database queries in real-time loops
- Cache frequently accessed data
- Use appropriate threading for I/O operations
- Profile code to identify bottlenecks

### Memory Management

- Release camera resources when not in use
- Close database connections properly
- Use context managers for resource management
- Monitor memory usage during long-running operations

## Deployment

### Production Considerations

- Use a production WSGI server (Gunicorn, uWSGI)
- Configure proper logging
- Set debug mode to False
- Use environment variables for configuration
- Implement proper error handling and monitoring

### Docker Deployment

A Dockerfile can be created for containerized deployment:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Download YOLO weights in Docker build
# ADD yolov3.weights /app/

EXPOSE 5000

CMD ["python", "app.py"]
```

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make changes and commit
4. Push to your fork
5. Create a pull request with description

### Code Review Guidelines

- Review for code quality and style
- Check for proper error handling
- Verify documentation is updated
- Ensure tests are included
- Confirm no security vulnerabilities

## Troubleshooting Development Issues

### Common Issues and Solutions

**Import Errors:**
- Check that all `__init__.py` files are present
- Verify Python path includes project directory
- Ensure virtual environment is activated

**Database Errors:**
- Check database file permissions
- Verify SQLite is properly installed
- Ensure database directory is writable

**Camera Access Issues:**
- Check camera permissions
- Verify camera is not in use by other applications
- Test camera with simple OpenCV script

**Web Interface Issues:**
- Check browser console for JavaScript errors
- Verify static file paths are correct
- Ensure Flask is serving static files properly

## Future Improvements

### Planned Features

- Unit test coverage
- Multi-camera support
- Advanced analytics dashboard
- Mobile-responsive design
- Internationalization support
- API authentication
- Configuration UI
- Historical data visualization

### Technical Debt

- Refactor detection logic for better modularity
- Improve error handling and logging
- Add comprehensive documentation
- Implement continuous integration
- Add performance monitoring
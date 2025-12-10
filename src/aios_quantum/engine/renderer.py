"""
WebGL Renderer

Exports engine state to HTML with WebGL visualization.
Creates a simple 3D scene: cube containing sphere,
with quantum data encoded as colors on the sphere surface.
"""

from pathlib import Path
from typing import Optional
import json

from .core import QuantumEngine


def generate_webgl_html(
    engine: QuantumEngine,
    title: str = "AIOS Quantum Visualization"
) -> str:
    """
    Generate standalone HTML with WebGL visualization.
    
    Uses Three.js for 3D rendering.
    """
    state = engine.get_state()
    
    # Convert surface data to JSON for JavaScript
    surface_json = json.dumps(state.surface_data)
    
    # Pre-compute display values
    coherence_val = f"{state.encoding_result['coherence']:.4f}" if state.encoding_result else 'N/A'
    entropy_val = f"{state.encoding_result['entropy']:.4f}" if state.encoding_result else 'N/A'
    dominant_val = state.encoding_result['dominant_state'] if state.encoding_result else 'N/A'
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ 
            background: #000; 
            overflow: hidden;
            font-family: 'Courier New', monospace;
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            color: #0ff;
            font-size: 14px;
            z-index: 100;
            background: rgba(0,0,0,0.7);
            padding: 15px;
            border: 1px solid #0ff;
        }}
        #info h1 {{
            font-size: 18px;
            margin-bottom: 10px;
            color: #fff;
        }}
        #info .metric {{
            margin: 5px 0;
        }}
        #info .value {{
            color: #0f0;
        }}
        #controls {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            color: #0ff;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h1>AIOS Quantum Engine</h1>
        <div class="metric">Cube: <span class="value">{state.cube_size}</span></div>
        <div class="metric">Sphere: <span class="value">{state.sphere_radius}</span></div>
        <div class="metric">Points: <span class="value">{len(state.surface_data)}</span></div>
        <div class="metric">Coherence: <span class="value" id="coherence">{coherence_val}</span></div>
        <div class="metric">Entropy: <span class="value" id="entropy">{entropy_val}</span></div>
        <div class="metric">Dominant: <span class="value" id="dominant">{dominant_val}</span></div>
    </div>
    <div id="controls">
        Drag to rotate | Scroll to zoom | Space to animate
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // Surface data from Python
        const surfaceData = {surface_json};
        
        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000011);
        
        const camera = new THREE.PerspectiveCamera(
            75, window.innerWidth / window.innerHeight, 0.1, 1000
        );
        camera.position.z = 4;
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        // Cube (wireframe)
        const cubeSize = {state.cube_size};
        const cubeGeometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize);
        const cubeMaterial = new THREE.MeshBasicMaterial({{
            color: 0x00ffff,
            wireframe: true,
            transparent: true,
            opacity: 0.3
        }});
        const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
        scene.add(cube);
        
        // Sphere surface points
        const sphereRadius = {state.sphere_radius};
        const pointsGeometry = new THREE.BufferGeometry();
        const positions = [];
        const colors = [];
        const sizes = [];
        
        surfaceData.forEach(point => {{
            positions.push(point.position[0], point.position[1], point.position[2]);
            colors.push(point.color[0], point.color[1], point.color[2]);
            sizes.push(point.intensity * 0.05 + 0.02);
        }});
        
        pointsGeometry.setAttribute('position', 
            new THREE.Float32BufferAttribute(positions, 3));
        pointsGeometry.setAttribute('color', 
            new THREE.Float32BufferAttribute(colors, 3));
        
        const pointsMaterial = new THREE.PointsMaterial({{
            size: 0.04,
            vertexColors: true,
            transparent: true,
            opacity: 0.9,
            sizeAttenuation: true
        }});
        
        const points = new THREE.Points(pointsGeometry, pointsMaterial);
        scene.add(points);
        
        // Inner sphere (translucent)
        const sphereGeometry = new THREE.SphereGeometry(sphereRadius * 0.95, 32, 32);
        const sphereMaterial = new THREE.MeshBasicMaterial({{
            color: 0x001122,
            transparent: true,
            opacity: 0.3,
            side: THREE.BackSide
        }});
        const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
        scene.add(sphere);
        
        // Axes helper (subtle)
        const axesSize = cubeSize * 0.6;
        const axesMaterial = new THREE.LineBasicMaterial({{ 
            color: 0x444444,
            transparent: true,
            opacity: 0.3 
        }});
        
        // X axis
        const xLine = new THREE.Line(
            new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(-axesSize, 0, 0),
                new THREE.Vector3(axesSize, 0, 0)
            ]),
            new THREE.LineBasicMaterial({{ color: 0x440000, opacity: 0.3, transparent: true }})
        );
        scene.add(xLine);
        
        // Y axis  
        const yLine = new THREE.Line(
            new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(0, -axesSize, 0),
                new THREE.Vector3(0, axesSize, 0)
            ]),
            new THREE.LineBasicMaterial({{ color: 0x004400, opacity: 0.3, transparent: true }})
        );
        scene.add(yLine);
        
        // Z axis
        const zLine = new THREE.Line(
            new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(0, 0, -axesSize),
                new THREE.Vector3(0, 0, axesSize)
            ]),
            new THREE.LineBasicMaterial({{ color: 0x000044, opacity: 0.3, transparent: true }})
        );
        scene.add(zLine);
        
        // Mouse controls
        let isDragging = false;
        let previousMousePosition = {{ x: 0, y: 0 }};
        let rotationSpeed = {{ x: 0.002, y: 0.002 }};
        let autoRotate = true;
        
        document.addEventListener('mousedown', () => {{ isDragging = true; }});
        document.addEventListener('mouseup', () => {{ isDragging = false; }});
        document.addEventListener('mousemove', (e) => {{
            if (isDragging) {{
                autoRotate = false;
                const deltaMove = {{
                    x: e.offsetX - previousMousePosition.x,
                    y: e.offsetY - previousMousePosition.y
                }};
                
                cube.rotation.y += deltaMove.x * 0.01;
                cube.rotation.x += deltaMove.y * 0.01;
                points.rotation.y += deltaMove.x * 0.01;
                points.rotation.x += deltaMove.y * 0.01;
                sphere.rotation.y += deltaMove.x * 0.01;
                sphere.rotation.x += deltaMove.y * 0.01;
            }}
            previousMousePosition = {{ x: e.offsetX, y: e.offsetY }};
        }});
        
        // Zoom
        document.addEventListener('wheel', (e) => {{
            camera.position.z += e.deltaY * 0.01;
            camera.position.z = Math.max(2, Math.min(10, camera.position.z));
        }});
        
        // Space to toggle animation
        document.addEventListener('keydown', (e) => {{
            if (e.code === 'Space') {{
                autoRotate = !autoRotate;
            }}
        }});
        
        // Animation loop
        function animate() {{
            requestAnimationFrame(animate);
            
            if (autoRotate) {{
                cube.rotation.y += 0.003;
                cube.rotation.x += 0.001;
                points.rotation.y += 0.003;
                points.rotation.x += 0.001;
                sphere.rotation.y += 0.003;
                sphere.rotation.x += 0.001;
            }}
            
            renderer.render(scene, camera);
        }}
        
        // Handle resize
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        animate();
    </script>
</body>
</html>'''
    
    return html


def export_webgl(
    engine: QuantumEngine,
    filepath: str,
    title: str = "AIOS Quantum Visualization"
):
    """Export engine state to HTML file with WebGL visualization."""
    html = generate_webgl_html(engine, title)
    Path(filepath).write_text(html, encoding='utf-8')
    return filepath


class WebGLRenderer:
    """
    WebGL renderer for the quantum engine.
    
    Generates standalone HTML files that can be opened in any browser.
    """
    
    def __init__(self, engine: QuantumEngine):
        self.engine = engine
    
    def render_to_file(
        self, 
        filepath: str,
        title: str = "AIOS Quantum Visualization"
    ) -> str:
        """Render current engine state to HTML file."""
        return export_webgl(self.engine, filepath, title)
    
    def render_to_string(self, title: str = "AIOS Quantum") -> str:
        """Render to HTML string."""
        return generate_webgl_html(self.engine, title)

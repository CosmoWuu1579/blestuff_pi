#!/usr/bin/env python3
"""Test if javaobj-py3 can read the calibration file"""

try:
    import javaobj
    print(f"javaobj version: {javaobj.__version__ if hasattr(javaobj, '__version__') else 'unknown'}")
    print(f"javaobj module: {javaobj.__file__}")
    
    filename = "./REFL_miniVNATiny.cal"
    print(f"\nTrying to read: {filename}")
    
    with open(filename, "rb") as f:
        # Try the new javaobj API
        try:
            # javaobj-py3 uses loads() for reading from bytes
            data = f.read()
            obj = javaobj.loads(data)
            print("Successfully loaded with javaobj.loads()")
            print(f"Object type: {type(obj)}")
            print(f"Object: {obj}")
        except Exception as e1:
            print(f"loads() failed: {e1}")
            
            # Try the old API
            f.seek(0)
            try:
                decoder = javaobj.JavaObjectUnmarshaller(f)
                version = decoder.readObject()
                print(f"Successfully read with JavaObjectUnmarshaller")
                print(f"Version: {version}")
            except Exception as e2:
                print(f"JavaObjectUnmarshaller failed: {e2}")
                
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
try:
    from routers import units
    print('Units module loaded successfully')
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f'Error loading units module: {e}')

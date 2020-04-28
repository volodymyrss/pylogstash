
def test_basic():
    import pylogstash 
    log_stasher = pylogstash.LogStasher()
    
    log_stasher.log({})

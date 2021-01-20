
def test_basic():
    import logging
    logging.basicConfig() #level=logging.DEBUG)
    logger = logging.getLogger("test")

    import pylogstash 


    log_stasher = pylogstash.LogStasher()

    logger.info("built logstash: %s", log_stasher)
    
    log_stasher.log({})

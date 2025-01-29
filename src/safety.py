class Safety:

    def __init__(
            self,
            WattLimit, 
            Wcount,
	        Hip_max, 
            Hip_min, 
            Thigh_max, 
            Thigh_min, 
            Calf_max, 
            Calf_min
                 ):
        pass

    def position_limit(self):
        """
         only effect under Low Level control in Position mode
        """
        pass
    
    def power_protect(self, limit):
        """
        only effect under Low Level control, input factor: 1~10, 
        means 10%~100% power limit. If you are new, then use 1; if you are familiar, 
        then can try bigger number or even comment this function.
        """
        pass

    def position_protect(self, limit = 0.087):
        """
        default limit is 5 degree
        """
        pass
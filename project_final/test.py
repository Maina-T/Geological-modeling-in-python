

class CalculateVolume:
    test =155
    entries = test

    def calculate_volume(self, estimated_block_value):
        volume_data = []
        for value in estimated_block_value:
            cut_off_grade = 42
            if value > cut_off_grade:
                volume = (value/self.entries) * 1000
                volume_data.append(volume)
        total_volume = sum(volume_data)
        print('\nTotal ore volume:', total_volume)
        tonnes_of_ore_to_be_mined = (total_volume) * 2.5
        print('Tonnes of ore to be mined:', tonnes_of_ore_to_be_mined)

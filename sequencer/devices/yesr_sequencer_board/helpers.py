from sequencer.devices.yesr_sequencer_board.exceptions import TimeOutOfBoundsError

def time_to_ticks(interval, time):
    ticks = int(round(time/interval))
    return ticks

def combine_sequences(subsequence_list):
    combined_sequence = subsequence_list.pop(0)
    for subsequence in subsequence_list:
        for k in subsequence.keys():
            combined_sequence[k] += subsequence[k]
    return combined_sequence


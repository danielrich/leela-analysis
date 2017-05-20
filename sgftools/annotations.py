from sgftools import sgflib

def insert_sequence(cursor, seq, data=None, callback=None):
    if data is None:
        data = [0]*len(seq)
    for (color, mv), elem in zip(seq, data):
        nnode = sgflib.Node()
        assert color in ['white', 'black']
        color = 'W' if color =='white' else 'B'
        nnode.addProperty( nnode.makeProperty(color, [mv]) )
        cursor.appendNode( nnode )
        cursor.next( len(cursor.children) - 1 )

        if callback is not None:
            if type(elem) in [list, tuple]:
                elem = list(elem)
            else:
                elem = [elem]
            callback( *tuple([cursor] + elem) )

    for i in xrange(len(seq)):
        cursor.previous()

def format_variation(cursor, seq):
    mv_seq = [(color, mv) for color, mv, _stats, _mv_list in seq]
    mv_data = [('black' if color == 'white' else 'white', stats, mv_list) for color, _mv, stats, mv_list in seq]
    insert_sequence(cursor, mv_seq, mv_data, format_analysis)

def format_pos(pos,board_size):
    if len(pos) != 2:
        return pos
    return (pos[0] + str(board_size - (ord(pos[1]) - ord('a')))).upper()

def format_winrate(stats,move_list,board_size):
    comment = ""
    if'winrate' in stats:
        comment += "Overall black win%%: %.2f%%\n" % (stats['winrate'] * 100)

    if len(move_list) > 0:
        comment += "Leela's next move: %s\n" % format_pos(move_list[0]['pos'],board_size)
    else:
        comment += "\n"

    return comment

def format_delta_info(delta, stats, this_move):
    comment = ""
    LB_values = []
    if(delta <= -0.10):
        comment += "==========================\n"
        comment += "BLUNDER!! (delta %.2f%%)\n" % (delta * 100)
        comment += "==========================\n"
        LB_values.append("%s:%s" % (this_move,":("))
    elif(delta <= -0.04):
        comment += "==========================\n"
        comment += "MISTAKE! (delta %.2f%%)\n" % (delta * 100)
        comment += "==========================\n"
        LB_values.append("%s:%s" % (this_move,":("))
    elif(delta <= -0.02):
        comment += "==========================\n"
        comment += "INACCURACY (delta %.2f%%)\n" % (delta * 100)
        comment += "==========================\n"
        LB_values.append("%s:%s" % (this_move,":("))
    elif(delta <= -0.001):
        comment += "(delta %.2f%%)\n" % (delta * 100)

    comment += "\n"
    return (comment,LB_values)

def format_analysis(stats, move_list):
    abet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    comment = ""
    if 'bookmoves' in stats:
        comment += "==========================\n"
        comment += "Considered %d/%d bookmoves\n" % (stats['bookmoves'], stats['positions'])
    else:
        comment += "==========================\n"
        comment += "Visited %d nodes\n" % (stats['visits'])
        comment += "\n"

        for L, mv in zip(abet, move_list):
            comment += "%s -> Win%%: %.2f%% (%d visits) \n" % (L, mv['winrate'] * 100, mv['visits'])

    LB_values = ["%s:%s" % (mv['pos'],L) for L, mv in zip(abet, move_list)]
    return (comment,LB_values)

def annotate_sgf(cursor, comment, LB_values):
    cnode = cursor.node
    if cnode.has_key('C'):
        cnode['C'].data[0] += comment
    else:
        cnode.addProperty( cnode.makeProperty( 'C', [comment] ) )

    if len(LB_values) > 0:
        cnode.addProperty( cnode.makeProperty( 'LB', LB_values ) )

import re
import math
import os
import sys
import pkg_resources
from argparse import Namespace

class ShannonScore:
    def __init__(self):
        self._kmers = {}
        self._kmers_phage = []
        self._kmers_all = []
        DATA_PATH = pkg_resources.resource_filename(__name__, 'data/')
        try:
            infile = open(DATA_PATH + 'mer_ORF_list.txt', 'r')
        except:
            sys.exit('ERROR: Cannot open ' + DATA_PATH + 'mer_ORF_list.txt')
        for line in infile:
            line = line.strip()
            self._kmers[line] = ''

    def reset(self):
        self._kmers_phage = []
        self._kmers_all = []

    def addValue(self, seq):
        mer = 12
        seq = seq.strip().upper()
        pos = 0
        self._kmers_phage.append([])
        self._kmers_all.append(0)
        while( pos <= (len(seq) - mer) ):
            substr = seq[pos:pos + mer]
            pos = pos + mer
            self._kmers_all[-1] += 1 
            try:            
                self._kmers[substr]
                self._kmers_phage[-1].append(substr)
            except KeyError:
                continue

    def getSlope(self, start, stop):
        total = sum(self._kmers_all[start : stop])
        found_total = sum([len(x) for x in self._kmers_phage[start : stop]])
        if total == 0:
            return 0
        H = 0.0
        window_kmers = {}
        for kl in self._kmers_phage[start : stop]:
            for k in kl:
                try:
                    window_kmers[k] += 1.0
                except KeyError:
                    window_kmers[k] = 1.0
        for i in window_kmers.values():
            p = i / total
            H = H + p * (math.log(p) / math.log(2))
        if H > 0:
            return 0
        freq_found = found_total / float(total)
        myslope = -freq_found / H
        return myslope

def read_contig(organismPath):
    try:
        f_dna = open(organismPath + '/contigs', 'r')
    except:
        print('cant open contig file ', organismPath)
        return ''
    dna = {}
    seq = ''
    name = ''
    for i in f_dna:
        if i[0] == '>':
            if len(seq) > 10:
                dna[name] = seq
            name = i.strip()
            if ' ' in name:
                temp = re.split(' ', name)
                name = temp[0]
            name = name[1:len(name)]
            seq = ''
        else:
            seq = seq + i.strip()
    dna[name] = seq
    f_dna.close()
    return dna

def my_sort(orf_list):
    n = len(orf_list)
    i = 0
    while i < n:
        j = i + 1
        while j < n:
            flag = 0
            # direction for both
            if orf_list[i]['start'] < orf_list[i]['stop']:
                dir_i = 1
            else:
                dir_i = -1
            if orf_list[j]['start'] < orf_list[j]['stop']:
                dir_j = 1
            else:
                dir_j = -1
            # check whether swap need or not
            if dir_i == dir_j:
                if orf_list[i]['start'] > orf_list[j]['start']:
                    flag = 1
            else:
                if dir_i == 1:
                    if orf_list[i]['start'] > orf_list[j]['stop']:
                        flag = 1
                else:
                    if orf_list[i]['stop'] > orf_list[j]['start']:
                        flag = 1
            # swap
            if flag == 1:
                temp = orf_list[i]
                orf_list[i] = orf_list[j]
                orf_list[j] = temp
            j += 1
        i += 1
    return orf_list

def find_all_median(orf_list):
    all_len = []
    for i in orf_list:
        all_len.append((abs(i['start'] - i['stop'])) + 1)
    return find_median(all_len)

def find_median(all_len):
    n = int(round(len(all_len) / 2))
    all_len.sort()
    if len(all_len) == n * 2:
        return (all_len[n] + all_len[n - 1]) / float(2)
    else:
        return all_len[n]

def find_atgc_skew(seq):
    seq = seq.upper()
    total_at = 0.0
    total_gc = 0.0
    a = 0
    t = 0
    c = 0
    g = 0
    for base in seq:
        if base == 'A':
            a += 1
            total_at += 1
        elif base == 'T':
            t += 1
            total_at += 1
        elif base == 'G':
            g += 1
            total_gc += 1
        elif base == 'C':
            c += 1
            total_gc += 1
        elif base == 'R':
            a += 0.5
            total_at += 0.5
            g += 0.5
            total_gc += 0.5
        elif base == 'Y':
            c += 0.5
            total_gc += 0.5
            t += 0.5
            total_at += 0.5
        elif base == 'S':
            g += 0.5
            total_gc += 0.5
            c += 0.5
            total_gc += 0.5
        elif base == 'W':
            a += 0.5
            total_at += 0.5
            t += 0.5
            total_at += 0.5
        elif base == 'K':
            g += 0.5
            total_gc += 0.5
            t += 0.5
            total_at += 0.5
        elif base == 'M':
            c += 0.5
            total_gc += 0.5
            a += 0.5
            total_at += 0.5
        elif base == 'B':
            c += 0.3
            total_gc += 0.3
            g += 0.3
            total_gc += 0.3
            t += 0.3
            total_at += 0.3
        elif base == 'D':
            a += 0.3
            total_at += 0.3
            g += 0.3
            total_gc += 0.3
            t += 0.3
            total_at += 0.3
        elif base == 'H':
            a += 0.3
            total_at += 0.3
            c += 0.3
            total_gc += 0.3
            t += 0.3
            total_at += 0.3
        elif base == 'V':
            a += 0.3
            total_at += 0.3
            c += 0.3
            total_gc += 0.3
            g += 0.3
            total_gc += 0.3
        elif base == 'N':
            a += 0.25
            total_at += 0.25
            t += 0.25
            total_at += 0.25
            g += 0.25
            total_gc += 0.25
            c += 0.25
            total_gc += 0.25
        else:
            print("seq", seq)
            print("base", base)
            sys.exit("ERROR: Non nucleotide base found")
    if(total_at * total_gc) == 0:
        print(seq)
        sys.exit("a total of zero total_at*total_gc")
    return float(a)/total_at, float(t)/total_at, float(g)/total_gc, float(c)/total_gc

def find_avg_atgc_skew(orf_list, mycontig, dna):
    a_skew = []
    t_skew = []
    g_skew = []
    c_skew = []
    for i in orf_list:
        start = i['start']
        stop = i['stop']
        if start < stop:
            bact = dna[mycontig][start - 1:stop]
            xa, xt, xg, xc = find_atgc_skew(bact)
        else:
            bact = dna[mycontig][stop - 1:start]
            xt, xa, xc, xg = find_atgc_skew(bact)
        if len(bact) < 3:
            continue
        a_skew.append(xa)
        t_skew.append(xt)
        g_skew.append(xg)
        c_skew.append(xc)
    return a_skew, t_skew, g_skew, c_skew

######################################################################################

def make_set_train(**kwargs):
    self = Namespace(**kwargs)
    my_shannon_scores = ShannonScore()
    all_orf_list = {}
    dna = {}
    window = 40
    for entry in self.record:
        dna[entry.id] = str(entry.seq)
        for feature in entry.get_features('CDS'):
            orf_list = all_orf_list.get(entry.id, [])
            is_phage = int(feature.qualifiers['is_phage'][0]) if 'is_phage' in feature.qualifiers else 0
            orf_list.append(
                   {'start' : feature.start,
                    'stop'  : feature.stop,
                    'peg'   : 'peg',
                    'is_phage': is_phage
                   }
            )
            all_orf_list[entry.id] = orf_list
    try:
        outfile = open(os.path.join(self.output_dir, self.make_training_data),'w')
    except:
        sys.exit('ERROR: Cannot open', os.path.join(self.output_dir, self.make_training_data), 'for writing.')
    outfile.write('orf_length_med\tshannon_slope\tat_skew\tgc_skew\tmax_direction\tstatus\n')
    for mycontig in all_orf_list:
        # orf_list = my_sort(all_orf_list[mycontig]) #shouldn't that be deleted as well?
        orf_list = all_orf_list[mycontig]
        ######################

        if not orf_list:
            continue

        all_median = find_all_median(orf_list)
        lengths = []
        directions = []
        for i in orf_list:
            lengths.append(abs(i['start'] - i['stop']) + 1) # find_all_median can be deleted now
            directions.append(1 if i['start'] < i['stop'] else -1)
            if i['start'] < i['stop']:
                seq = dna[mycontig][i['start'] - 1 : i['stop']]
            else:
                seq = dna[mycontig][i['stop'] - 1 : i['start']]
            my_shannon_scores.addValue(seq)

        ga_skew, gt_skew, gg_skew, gc_skew = find_avg_atgc_skew(orf_list, mycontig, dna)
        a = sum(ga_skew) / len(ga_skew)
        t = sum(gt_skew) / len(gt_skew)
        g = sum(gg_skew) / len(gg_skew)
        c = sum(gc_skew) / len(gc_skew)
        avg_at_skew, avg_gc_skew = math.fabs(a - t), math.fabs(g - c)
        #####################
        i = 0
        # while i<len(orf_list)-window +1:
        while i < len(orf_list):
            #initialize
            j_start = i - int(window / 2)
            j_stop = i + int(window / 2)
            if j_start < 0:
                j_start = 0
            elif j_stop >= len(orf_list):
                j_stop = len(orf_list)
            # at and gc skews
            ja_skew = ga_skew[j_start:j_stop]
            jt_skew = gt_skew[j_start:j_stop]
            jc_skew = gc_skew[j_start:j_stop]
            jg_skew = gg_skew[j_start:j_stop]
            ja = sum(ja_skew) / len(ja_skew)
            jt = sum(jt_skew) / len(jt_skew)
            jc = sum(jc_skew) / len(jc_skew)
            jg = sum(jg_skew) / len(jg_skew)
            jat = math.fabs(ja - jt) / avg_at_skew if avg_at_skew else 0
            jgc = math.fabs(jg - jc) / avg_gc_skew if avg_gc_skew else 0
            my_length = find_median(lengths[j_start:j_stop]) - all_median
            # orf direction
            orf = []
            x = 0
            flag = 0
            for ii in directions[j_start:j_stop]:
                if ii == 1:
                    if flag == 0 :
                        x += 1
                    else:
                        orf.append(x)
                        x = 1
                        flag = 0
                else:
                    if flag == 1:
                        x += 1
                    else:
                        if flag < 1 and x > 0:
                            orf.append(x)
                        x = 1
                        flag = 1
            orf.append(x)
            orf.sort()
            outfile.write(str(my_length))
            outfile.write('\t')
            outfile.write(str(my_shannon_scores.getSlope(j_start, j_stop)))
            outfile.write('\t')
            outfile.write(str(jat))
            outfile.write('\t')
            outfile.write(str(jgc))
            outfile.write('\t')
            outfile.write(str(orf[len(orf) - 1]) if len(orf) == 1 else str(orf[len(orf) - 1] + orf[len(orf) - 2]))
            outfile.write('\t')
            outfile.write('1' if orf_list[i]['is_phage'] else '0')
            outfile.write('\n')
            i += 1
        my_shannon_scores.reset()
    outfile.close()
import argparse
import math

# Load input data
parser = argparse.ArgumentParser()
parser.add_argument('--sex ', help = 'Gender of the patient, where male = 1 and female = 0', required = True, dest="sex")
parser.add_argument('--age ', help = 'Age (in years) of the patient', required = True, dest="age")
parser.add_argument('--symp_gr3', help = 'symp_gr3toms, where Non-typical angina=0, Atypical angina or dyspnoea=1 and Typical angina =2', required = True, dest="symp_gr3")
parser.add_argument('--nb_rf ', help = 'Number of risk factors (0-5) (riskfactors: Family history of early CAD, Smoking, Dyslipidaemia, Hypertension or Diabetes)', dest="nb_rf")
parser.add_argument('--cacs', help = 'Coronary artery calcium score determined by the Agatston method', dest="cacs")
args = parser.parse_args()

def write_report(sex, age, symp_gr3, nb_rf, cacs, ptp_basic, ptp_rf, ptp_cacs):
    title = f"#### CAD-PTP: Estimation of Clinical likelihood of coronary artery disease"


    # get label for the sympthoms
    if symp_gr3 == 0:
        symp = "Non-typical angina (0)"

    elif symp_gr3 == 1:
        symp = "Atypical angina or dyspnoea (1)"

    elif symp_gr3 == 2:
        symp = "Typical angina (2)"
    else:
        print("Error in the sympthoms")

    # get label for the sex
    if sex == 0:
        sex_var = "Male (0)"

    elif sex == 1:
        sex_var = "Female (1)"
        
    else:
        print("Error in the sex")

    patient_info = f"Entered patient information\n\n| Feature | Value |\n| --- | ---: |\n|**Sex** | {sex_var} |\n|**Age** | {age} |\n|**Sympthoms** | {symp} |\n|**Number of risk factors** | {nb_rf} |\n|**Coronary artery calcium score (CACS)** | \t{cacs} |\n"

    cadptp_info = f"Coronary risk estimation(*)\n\n| CL | Risk |\n| --- | ---: |\n|**Basic-CL** | {round(ptp_basic*100, 2)}% ({round(ptp_basic,4)}) |\n|**RF-CL** | {round(ptp_rf*100, 2)}% ({round(ptp_rf,4)})|\n| **CACS-CL** | {round(ptp_cacs*100, 2)}% ({round(ptp_cacs,4)})|\n"

    # get final risk
    risk = round(ptp_basic * 100, 2)
    label = "Basic-CL"

    percent_basic = round(ptp_basic * 100, 2)
    decimal_basic = round(ptp_basic, 4)

    percent_rf = "-"
    decimal_rf = "-"

    percent_cacs = "-"
    decimal_cacs = "-"

    if ptp_rf >=  0:
        percent_rf = round(ptp_rf * 100, 2)
        decimal_rf = round(ptp_rf, 4)
        if percent_rf > risk:
            risk = percent_rf
            label = "RF-CL"
        if ptp_cacs > 0:
            percent_cacs = round(ptp_cacs * 100, 2)
            decimal_cacs = round(ptp_cacs, 4)
            if percent_cacs > risk:
                risk = percent_cacs
                label = "CACS-CL"


    final_risk = f"The final risk is {label}, **{risk}%**. "

    footnote = f"(*)The Basic-CL refers to basic clinical likelihood calculated only through pre-test probability (PTP). RF-CL refers to risk factor–weighted clinical likelihood calculated through PTP and risk factors. CACS-CL refers to CACS–weighted clinical likelihood is calculated through PTP,risk factors and CACS"

    report = f"{title}\n\n***\n\n{patient_info}\n***\n\n\n{cadptp_info}\n\n{final_risk}\n\n***\n\n{footnote}\n"

    # Print report
    print(report)

    # Save report as Markdown document
    with open('report.md', 'w') as txt:
        txt.write(report)


def cadptp(sex, age, symp_gr3, nb_rf, cacs):
    """ Function from Samuel Emil Schmidt, and Simon Winther translated from R to Python """

    # One-hot encoding of the symp_gr3toms
    if symp_gr3 == 0: symp_non_anglinal = 1
    else: symp_non_anglinal = 0

    if symp_gr3 == 2: symp_typical = 1
    else: symp_typical = 0

    # Basic PTP
    ptp_basic = 1. / (1 + math.exp(-(-7.0753 + (1.2308 * sex) + (0.0642 * age) + (2.2501 * symp_typical) + (-0.5095 * symp_non_anglinal) + (-0.0191 * age * symp_typical))))

    # If number of risk factors is available
    ptp_rf = "None"
    if nb_rf is not None:
        nb_rf = int(nb_rf)
        nb_rf_3 = (nb_rf >= 0) + (nb_rf >= 2) + (nb_rf >= 4)
        ptp_rf = 1. / (1 + math.exp(-(-9.5260 + (1.6128 * sex) + (0.08440 * age) + (2.7112 * symp_typical) + (-0.4675 *symp_non_anglinal) + (1.4940 * nb_rf_3) + (-0.0187 * age * symp_typical) + (-0.0131 * age * nb_rf_3) + (-0.2799 * symp_typical * nb_rf_3) + (-0.2091 * sex * nb_rf_3))))

    ptp_cacs = "None"
    if cacs is not None:
        cacs = int(cacs)
        cacs_1_9 = cacs >= 1 and cacs < 10
        cacs_10_99 = cacs >= 10 and cacs < 100
        cacs_100_399 = cacs >= 100 and cacs < 400
        cacs_400_999 = cacs >= 400 and cacs < 1000
        cacs_1000 = cacs >= 1000
        
        ptp_cacs = 0.0013 + (ptp_rf * 0.2021) + (cacs_1_9 * 0.0082) + (cacs_10_99 *0.0238) + (cacs_100_399 * 0.1131) + (cacs_400_999 * 0.2306) + (cacs_1000 * 0.4040) + (ptp_rf * cacs_1_9 * 0.1311) + (ptp_rf * cacs_10_99 * 0.2909) + (ptp_rf * cacs_100_399 * 0.4077) + (ptp_rf * cacs_400_999 * 0.4658) + (ptp_rf * cacs_1000 * 0.4489)

    write_report(sex, age, symp_gr3, nb_rf, cacs, ptp_basic, ptp_rf, ptp_cacs)


def main():
    sex = int(args.sex)
    age = float(args.age)
    symp_gr3 = int(args.symp_gr3)
    nb_rf = args.nb_rf
    cacs = args.cacs

    cadptp(sex,age,symp_gr3,nb_rf,cacs)

if __name__ == "__main__":
    main()
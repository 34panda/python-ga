import numpy as np


def popinit(lg, lch):
    xp = np.random.randint(2, size=(lch, lg))
    return xp


def ocena(xp, wartosc, waga):
    ocena_populacji = np.sum(xp * wartosc, axis=1)
    waga_chromosomu = np.sum(xp * waga, axis=1)

    return (ocena_populacji, waga_chromosomu)


def wczytaj_z_plikow(lg, plik_waga="wag1.txt", plik_wartosci="wart1.txt"):
    wartosci = np.loadtxt(plik_wartosci)[:lg]
    wagi = np.loadtxt(plik_waga)[: lg + 1]

    return wartosci, wagi


def wczytaj_od_uzytkownika():
    lch = int(input("liczba chromosomow (limit = 50): "))
    lch = min(lch, 50)
    if lch % 2 != 0:
        lch += 1

    lg = int(input("liczba genow (limit = 10): "))
    lg = min(lg, 10)
    lpop = int(input("liczba populacji(limit = 500): "))
    lpop = min(lpop, 500)
    pm = float(input("prawdopodobienstwo mutacji (0 - 0.1): "))
    pm = min(pm, 0.1)
    pk = float(input("prawdopodobienstwo krzyzowania (0.6 - 1.0): "))
    pk = min(pk, 0.8)

    return (lch, lg, lpop, pm, pk)



def zapis(
    iteracja,
    ocena_populacji,
    najlepszy_chromosom,
    najlepsza_ocena,
    najlepsza_waga,
    znaleziono_nowy_najlepszy,
    nazwa_pliku="47324-hist.txt",
):

    min_fp = round(np.min(ocena_populacji))
    max_fp = round(np.max(ocena_populacji))
    sr_fp = round(np.mean(ocena_populacji), 2)

    with open(nazwa_pliku, "a", encoding="utf-8") as f:
        f.write(
            f"populacja={iteracja:03d}; min={min_fp:03d}; max={max_fp:03d}; sr={sr_fp:.2f}"
        )
        if najlepszy_chromosom is not None and znaleziono_nowy_najlepszy is True:
            f.write(
                f"; najlepszy={najlepszy_chromosom.tolist()}; fp={najlepsza_ocena}; waga={najlepsza_waga:.2f}"
            )
        f.write("\n")


def rodzice(xp, ocena_populacji, waga_populacji, waga_max):
    nrxp = []
    for _ in range(len(xp)):
        ch1, ch2 = np.random.choice(len(xp), 2, replace=False)
        (waga_ch1, waga_ch2) = (waga_populacji[ch1], waga_populacji[ch2])

        # Przekroczone obie wagi
        if waga_ch1 > waga_max and waga_ch2 > waga_max:
            wybrany = (
                ch1 if abs(waga_ch1 - waga_max) < abs(waga_ch2 -
                                                      waga_max) else ch2
            )

        # ch1 jest ponizej wagi_max, a ch2 powyzej
        elif waga_ch1 <= waga_max < waga_ch2:
            wybrany = ch1

        # ch2 jest ponizej wagi_max, a ch1 powyzej
        elif waga_ch2 <= waga_max < waga_ch1:
            wybrany = ch2
        else:
            wybrany = ch1 if ocena_populacji[ch1] > ocena_populacji[ch2] else ch2

        nrxp.append(wybrany)

    return nrxp


def mutuj(xp, pm):
    for i, chromosom in enumerate(xp, 1):
        for j, gen in enumerate(chromosom):
            p = np.random.random()
            if p < pm:
                chromosom[j] ^= 1
    return xp


def potomek(xp, pk):
    lg = xp.shape[1]
    xp_kopia = xp.copy()

    for i in range(0, len(xp) - 1, 2):
        p = np.random.random()
        if p < pk:
            if lg > 1:
                punkt_ciecia = np.random.randint(1, lg)
                xp_kopia[i, punkt_ciecia:], xp_kopia[i + 1, punkt_ciecia:] = (
                    xp[i + 1, punkt_ciecia:].copy(),
                    xp[i, punkt_ciecia:].copy(),
                )
            else:
                xp_kopia[i], xp_kopia[i + 1] = xp[i], xp[i + 1]

    return xp_kopia


if __name__ == "__main__":

    # Wczytanie parametrow
    (lch, lg, lpop, pm, pk) = wczytaj_od_uzytkownika()

    print("\nAlgorytm w toku...\n\n")

    # Wczytanie danych z plikow
    (wartosci, wagi) = wczytaj_z_plikow(lg)
    waga_max = wagi[0]

    # Inicjalizacja populacji
    xp = popinit(lg, lch)
    ocena_populacji, suma_wag_chromosomow = ocena(xp, wartosci, wagi[1:])

    # Wyszukiwanie najleoszego chrmosomu
    najlepszy_chromosom, najlepszy_chromosom1 = None, None
    najlepsza_ocena, najlepsza_ocena1 = 0, 0
    najlepsza_waga, najlepsza_waga1 = 0, 0
    najlepsza_iteracja, najlepsza_iteracja1 = 0, 0
    znaleziono_nowy_najlepszy, znaleziono_nowy_najlepszy1 = False, False

    # Wyczysc plik z poprzednich sesji
    with open("47324-hist.txt", "w", encoding="utf-8") as f:
        f.write(
            "populacja;min_fp;max_fp;sr_fp;najlepszy_ch;najlepsza_ocena_ch;najlepsza_waga_ch\n"
        )

    # Petla glowna
    for i in range(1, lpop + 1):
        # print(f"\nPopulacja {i}")

        # Rodzicoe
        indeksy_rodzicow = rodzice(
            xp, ocena_populacji, suma_wag_chromosomow, waga_max)
        xp = xp[indeksy_rodzicow]

        # Mutacja
        xp = mutuj(xp, pm)

        # Krzyzowanie
        xp = potomek(xp, pk)

        # Ocenianie populacji
        (ocena_populacji, suma_wag_chromosomow) = ocena(xp, wartosci, wagi[1:])

        # Aktualizacja najlepszego rozwiazania
        prawidlowe_indeksy1 = np.where(suma_wag_chromosomow <= waga_max)[0]
        if prawidlowe_indeksy1.size > 0:
            maksymalny_indeks1 = prawidlowe_indeksy1[
                np.argmax(ocena_populacji[prawidlowe_indeksy1])
            ]
            if ocena_populacji[maksymalny_indeks1] > najlepsza_ocena1:
                najlepsza_ocena1 = ocena_populacji[maksymalny_indeks1]
                najlepszy_chromosom1 = xp[maksymalny_indeks1]
                najlepsza_waga1 = suma_wag_chromosomow[maksymalny_indeks1]
                najlepsza_iteracja1 = i
                znaleziono_nowy_najlepszy1 = True
        znaleziono_nowy_najlepszy1 = False

        #########

        prawidlowe_indeksy = np.where(suma_wag_chromosomow <= waga_max)[0]
        if prawidlowe_indeksy.size > 0:
            maksymalny_indeks = prawidlowe_indeksy[
                np.argmax(ocena_populacji[prawidlowe_indeksy])
            ]
            najlepsza_ocena = ocena_populacji[maksymalny_indeks]
            najlepszy_chromosom = xp[maksymalny_indeks]
            najlepsza_waga = suma_wag_chromosomow[maksymalny_indeks]
            najlepsza_iteracja = i
            znaleziono_nowy_najlepszy = True

        zapis(
            i,
            ocena_populacji,
            najlepszy_chromosom,
            najlepsza_ocena,
            najlepsza_waga,

            znaleziono_nowy_najlepszy,
        )

        znaleziono_nowy_najlepszy = False

    # Wyswietlenie najlepszego dopuszczalnego rozwiazania i zapisanie do pliku
    with open("47324-hist.txt", "a", encoding="utf-8") as f:
        f.write(
            f"najlepszy_dopuszczalny_ch_ze_wszystkich_populacji={najlepszy_chromosom1}; fp={najlepsza_ocena1}; waga={najlepsza_waga1}; pierwsze_wystapienie_w_populacji_nr={najlepsza_iteracja1}"
        )
    print(f"Najlepszy dopuszczalny chromosom ze wszystkich populacji: ")
    print(f"{najlepszy_chromosom1}, fp={najlepsza_ocena1}, waga={najlepsza_waga1}, pierwsze wystapienie w populacji nr {najlepsza_iteracja1}")

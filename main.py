import concurrent.futures
from PIL import Image, ImageChops
from pathlib import Path


def clone_search(path, arr_copy, start):
    first = Image.open(path)

    ohana2 = []
    hit2 = []

    for g in range(0, len(arr_copy)):
        if path == arr_copy[g]:
            continue
        second = Image.open(arr_copy[g])
        diff = ImageChops.difference(first.convert("RGB"), second.convert("RGB"))
        if not diff.getbbox():
            ohana2.append(arr_copy[g])
            hit2.append(g + start)
        second.close()

    print("PROCESS DONE")
    return ohana2, hit2


def main():
    picDir = input("Enter the directory: ") or r"./clone test"

    my_path = Path(picDir)

    # Define allowed image extensions
    image_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    # Find all image files recursively
    arr = [str(p) for p in my_path.rglob("*") if p.suffix.lower() in image_extensions]

    print(arr, len(arr))

    arr_copy = arr.copy()

    # images that are found to be the same
    groups = []

    count = 0

    with concurrent.futures.ProcessPoolExecutor() as executor:
        print("MUTLIPROCESS START")
        n = len(arr_copy)
        k = 4
        

        while len(arr_copy) > 1 and count <= len(arr_copy):
            # leave if 1 or less

            print("SIZE: ", len(arr_copy))

            # ohana is a list of images that have dopplegangers
            ohana = []
            # hit is an index of where the doppelgangers are in the original list
            hit = []
            
            # a list of arrays split into k from the duplicated array
            splits  = []

            print("SPLITS: ", splits)
            for i in range(k):
                crop = arr_copy[
                    i * (n // k) + min(i, n % k) : (i + 1) * (n // k)
                    + min(i + 1, n % k)
                ]
                start = i * (n // k) + min(i, n % k)

                splits.append(executor.submit(clone_search, arr_copy[count], crop, start))

            for f in concurrent.futures.as_completed(splits):
                ohana_res, hit_res = f.result()

                if len(ohana_res):
                    ohana += ohana_res

                    hit += hit_res

            if len(ohana) > 0:
                ohana.append(arr_copy[count])
                hit.append(count)

                groups.append(ohana)
                count = 0

            else:
                # TEST
                arr_copy = arr_copy[1::]

                count += 1

            hit = list(set(hit))

            # hit exists if ohana exists.
            if len(hit) > 0:
                hit.sort(reverse=True)
                for i in hit:
                    print(arr_copy.pop(i))
                print("HITS", hit)
                print("OHANA CHECK ", ohana)

            print(groups)

            print("Clone detection: ", len(groups) >= 1)
            print()
    with open("log.txt", "w") as f:
        for i, x in enumerate(groups):
            f.write("[" + "Group: " + str(i) + "]" + "\n")

            for g in x:
                f.write(g + "\n")


if __name__ == "__main__":
    main()

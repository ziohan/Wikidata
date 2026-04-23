def save_txt(data, triples_labels_df):  

    chosen_labels = data.loc[
        data["Labels"].apply(lambda x: "Earth" in x),
        "Labels"
    ].iloc[0]

    print(chosen_labels)

    with open("output.txt", "w", encoding="utf-8") as f:
        for label in chosen_labels:
            f.write(f"{label}:")

            output_triple_text = triples_labels_df.loc[
                triples_labels_df["subject_label"] == label,
                "triple_text"
            ].tolist()

            for triple_text in output_triple_text:
                f.write(triple_text + "\n")

            f.write("\n")
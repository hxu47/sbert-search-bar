import traceback
import sys

def execute():
    try:
        # import libraries
        from src import processing, dataset, utils, embeddings, config
        import faiss
        import numpy as np
        import datetime
        import os

        print(f"-------- Start Training Search Index: {datetime.datetime.now()} --------")

        # 0. Check for required directories and create if not present
        os.makedirs(config.DIR_OUTPUT, exist_ok=True)
        os.makedirs(config.DIR_DATA, exist_ok=True)

        # 1. getting project description data 
        project_description_df = dataset.get_project_description()


        # 2. Video titles data
        project_topics_df = dataset.get_video_titles()

        # 3. Abbreviations Data
        abbreviations_df = dataset.get_abbreviations()


        # 4. Generate overall training data
        raw_data = utils.generate_data(project_description_df, project_topics_df)
        print("Raw data generated!")

        # 5. save project mappings csv for inference
        raw_data[['title']].to_csv(f"data/project_mappings.csv", index=False)
        print("Project mappings saved to query the results!" + f"\npath: data/project_mappings.csv")

        # 6. define abbreviation dic to complete preprocessing (Add context)
        abb_dic = utils.get_abbreviation_mapping(abbreviations_df)
        print("Abbreviations data read!")

        # 7. data preprocessing
        df= processing.final_preprocessing(raw_data,content_col='Description', abb_dic=abb_dic)
        print("Data preprocessing done!")

        
        # 8. generate embeddings
        # for all the projects
        descriptions=[]
        for i in df.index:
            descriptions.append(df['Processed_text'][i])
        
        des_emb = embeddings.create_embeddings(descriptions)
        print("Embeddings created!")

        # 9. generate FAISS
        encoded_data = np.asarray(des_emb.astype('float32'))
        # no of dimensions in encoded data - len(sen_emb[0])
        index = faiss.IndexIDMap(faiss.IndexFlatIP(len(des_emb[0])))
        index.add_with_ids(encoded_data, np.array(range(0, len(df))).astype(np.int64))
        # save index
        faiss.write_index(index, f'output/search.index')
        print("FAISS index generated and saved in output!")
        print(f"-------- Done Training Search Index: {datetime.datetime.now()} --------")
    except:
        print("Error in training search index!")
        print(traceback.format_exc())
        sys.exit(-1)

if __name__ == "__main__":
    execute()
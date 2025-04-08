import os

def vectorstore_path_tester(vectorstore_name: str):

    vectorstore_path = 'data/vectordb_' + vectorstore_name
    dir_path = os.path.dirname(os.path.realpath(__file__)) 
    # os.path.dirname(path) returns the directory name of the pathname "path"
    # os.path.realpath(path) return the cannonical path of the specified filename, eliminating any symbolic links encountered in the path.
    cwd = os.getcwd()
    output_list = [vectorstore_path, dir_path, cwd]

    if os.path.exists(vectorstore_path):
        # print(f'path {vectorstore_path} exists')
        output_list.append(f'path {vectorstore_path} exists')

    else:
        # print(f'path {vectorstore_path} does not exist')
        output_list.append(f'path {vectorstore_path} does not exist')

    return output_list

if __name__ == "__main__":
    for items in vectorstore_path_tester('email_semantic_98'):
        print(items)

    print('\n')
    for items in vectorstore_path_tester('email_semantic_100'):
        print(items)
    
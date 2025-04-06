import pandas as pd
from utils import board_matrix, q, MAX_TIME_LIMIT, WIDTH, HEIGHT


def load_questions(file_name):
  
    try:
        df = pd.read_csv(file_name, header=0)
        for i, row in enumerate(df['Row']):
            question = str(df["Question"][i])
            answer = str(df["Answer"][i])
            q[(row, df['Col'][i])] = {"question": question, "answer": answer}
        
        # Update categories
        for i, cat in enumerate(range(6)):
            if i < len(df['Categories']):
                board_matrix[0][i] = df['Categories'][i]
            else:
                board_matrix[0][i] = f"Category {i+1}"
                
    except Exception as e:
        print(f"Error loading questions: {e}")
        # Fallback to default questions
        board_matrix[0] = ["Category 1", "Category 2", "Category 3", 
                          "Category 4", "Category 5", "Category 6"]
    return q, board_matrix

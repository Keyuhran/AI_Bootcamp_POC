from openai import OpenAI

client = OpenAI()

job = client.fine_tuning.jobs.create(
    training_file="file-UoFH7Sz8KTgJV7cjuam1X1", 
    model="gpt-4o-mini-2024-07-18",
    method={
        "type": "supervised",
        "supervised": {
            "hyperparameters": {
                "n_epochs": 6
            }
        }
    }
)

print("Fine-tuning job started:", job.id)

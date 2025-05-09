from openai import OpenAI

client = OpenAI()

job = client.fine_tuning.jobs.retrieve("ftjob-XDmXTZekZ1O43Bs2tsZBNVT6")
print(job.status)

print(job.fine_tuned_model)

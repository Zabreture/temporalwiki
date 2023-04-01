#%%
import wandb
import random
wandb.init(
        project="icdcs23-poster",
        config={
            "learning_rate": 0.02,
            "architecture": "CNN",
            "dataset": "CIFAR-100",
            "epochs": 10,
        }
    )

# wandb_logger = WandbLogger(project=hparam.wandb_project, name=hparam.wandb_run_name, entity="nwpu")
epochs = 10
offset = random.random() / 5
for epoch in range(2, epochs):
    acc = 1 - 2 ** -epoch - random.random() / epoch - offset
    loss = 2 ** -epoch + random.random() / epoch + offset

    wandb.log({"acc": acc, "loss": loss})

wandb.finish()
print('Yes')

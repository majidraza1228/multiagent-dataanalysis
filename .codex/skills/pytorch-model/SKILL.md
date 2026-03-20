---
name: pytorch-model
description: PyTorch CNN scaffold for CIFAR-10 image classification with training loop, early stopping, and checkpointing
---

```python
# model/cnn.py
import torch
import torch.nn as nn

class SmallCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.pool = nn.AdaptiveAvgPool2d((2, 2))
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 4, 256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.pool(self.features(x)))
```

```python
# model/train.py
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import mlflow

from model.cnn import SmallCNN

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
EPOCHS = 50
BATCH = 128
LR = 1e-3
PATIENCE = 5

transform_train = transforms.Compose([
    transforms.RandomHorizontalFlip(), transforms.RandomCrop(32, padding=4),
    transforms.ToTensor(), transforms.Normalize((0.5,)*3, (0.5,)*3),
])
transform_val = transforms.Compose([
    transforms.ToTensor(), transforms.Normalize((0.5,)*3, (0.5,)*3),
])

train_ds = datasets.CIFAR10("data/", train=True, download=True, transform=transform_train)
val_ds   = datasets.CIFAR10("data/", train=False, download=True, transform=transform_val)
train_loader = DataLoader(train_ds, batch_size=BATCH, shuffle=True, num_workers=4)
val_loader   = DataLoader(val_ds,   batch_size=BATCH, shuffle=False, num_workers=4)

model = SmallCNN().to(DEVICE)
optimizer = Adam(model.parameters(), lr=LR)
scheduler = CosineAnnealingLR(optimizer, T_max=EPOCHS)
criterion = nn.CrossEntropyLoss()

mlflow.autolog()

best_acc, patience_count = 0.0, 0

with mlflow.start_run():
    for epoch in range(1, EPOCHS + 1):
        # --- train ---
        model.train()
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            loss = criterion(model(imgs), labels)
            loss.backward()
            optimizer.step()
        scheduler.step()

        # --- validate ---
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                preds = model(imgs).argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
        val_acc = correct / total
        print(f"Epoch {epoch:02d} | val_acc={val_acc:.4f}")

        # --- checkpoint & early stopping ---
        if val_acc > best_acc:
            best_acc = val_acc
            patience_count = 0
            torch.save(model, "checkpoints/model.pt")
        else:
            patience_count += 1
            if patience_count >= PATIENCE:
                print(f"Early stopping at epoch {epoch}")
                break
```

```python
# load checkpoint
import torch
model = torch.load("checkpoints/model.pt", map_location="cpu")
model.eval()
```

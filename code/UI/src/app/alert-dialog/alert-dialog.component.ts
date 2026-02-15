import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-alert-dialog',
  imports: [],
  templateUrl: './alert-dialog.component.html',
  styleUrl: './alert-dialog.component.scss'
})
export class AlertDialogComponent {
  title: string = '';
  message: string = '';

  constructor(public dialogRef: MatDialogRef<AlertDialogComponent>) {}

  showMessage(title: string,message: string): void {
    this.title = title;
    this.message = message;
  }

  onClose(): void {
    this.dialogRef.close();
  }
}

import { Component } from '@angular/core';
import { LoadingSpinnerComponent } from '../loading-spinner/loading-spinner.component';
import { CommonModule } from '@angular/common';
import { DataDisplayComponent } from '../data-display/data-display.component';
import { RouterOutlet } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { AlertDialogComponent } from '../alert-dialog/alert-dialog.component';
import { MatButtonModule } from '@angular/material/button';




@Component({
  selector: 'app-file-upload',
  imports: [LoadingSpinnerComponent,CommonModule,DataDisplayComponent,RouterOutlet,MatButtonModule],
  templateUrl: './file-upload.component.html',
  styleUrl: './file-upload.component.scss'
})
export class FileUploadComponent {
  file1: File | null = null;
  file2: File | null = null;
  isLoading = false;
  displayData:any=[];

  constructor(private dialog: MatDialog) {}
  
  onFileSelected(event: Event, fileNumber: number): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      if (file.type !== 'text/csv') {
        this.openDialog('Alert','Please select a CSV file.');
        input.value = ''; 
        return;
      }
      if (fileNumber === 1) {
        this.file1 = input.files[0];
      } else if (fileNumber === 2) {
        this.file2 = input.files[0];
      }
    }
  }

  onReconciliation(): void {
    if (this.file1 && this.file2) {
      // Perform reconciliation logic here
      this.isLoading = true;
    
      console.log('Reconciliation started with files:', this.file1.name, this.file2.name);
      this.displayData= [
        {
          "As of Date": "31-05-2024",
          "Company": 0,
          "Account": 1619288,
          "AU": 5701,
          "Currency": "USD",
          "Primary Account": "ALL OTHER LOANS",
          "Secondary Account": "DEFERRED ORIGINATION FEES",
          "GL Balance": 100000,
          "IHub Balance": 10000,
          "Balance Difference": 90000,
          "Match Status": "Break",
          "Anomaly Explanation": "Pattern deviation detected",
          "Confirmed Anomaly": "Pending Review",          
          "Action":""
        },
        {
          "As of Date": "31-05-2024",
          "Company": 2,
          "Account": 1619205,
          "AU": 4929,
          "Currency": "EUR",
          "Primary Account": "ALL OTHER LOANS",
          "Secondary Account": "PRINCIPAL",
          "GL Balance": 100000,
          "IHub Balance": 80000,
          "Balance Difference": -10000,
          "Match Status": "Break",
          "Anomaly Explanation": "GL Balance jumped from 60000.00 to 100000.00",
          "Confirmed Anomaly": "Pending Review",          
          "Action":""
        },
        {
          "As of Date": "30-06-2024",
          "Company": 0,
          "Account": 1619288,
          "AU": 5701,
          "Currency": "USD",
          "Primary Account": "ALL OTHER LOANS",
          "Secondary Account": "DEFERRED ORIGINATION FEES",
          "GL Balance": 100000,
          "IHub Balance": 10000,
          "Balance Difference": 90000,
          "Match Status": "Break",
          "Anomaly Explanation": "Pattern deviation detected",
          "Confirmed Anomaly": "Pending Review",          
          "Action":""
        },
        {
          "As of Date": "30-06-2024",
          "Company": 2,
          "Account": 1619205,
          "AU": 4929,
          "Currency": "EUR",
          "Primary Account": "ALL OTHER LOANS",
          "Secondary Account": "PRINCIPAL",
          "GL Balance": 80000,
          "IHub Balance": 90000,
          "Balance Difference": -10000,
          "Match Status": "Break",
          "Anomaly Explanation": "Pattern deviation detected",          
          "Confirmed Anomaly": "Pending Review",
          "Action":""
        },
        {
          "As of Date": "31-07-2024",
          "Company": 0,
          "Account": 1619288,
          "AU": 5701,
          "Currency": "USD",
          "Primary Account": "ALL OTHER LOANS",
          "Secondary Account": "DEFERRED ORIGINATION FEES",
          "GL Balance": 100000,
          "IHub Balance": 10000,
          "Balance Difference": 90000,
          "Match Status": "Break",
          "Anomaly Explanation": "Pattern deviation detected",  
          "Confirmed Anomaly": "Pending Review",
          "Action":""
        },
        {
          "As of Date": "31-07-2024",
          "Company": 2,
          "Account": 1619205,
          "AU": 4929,
         "Currency": "EUR",
         "Primary Account": "ALL OTHER LOANS",
          "Secondary Account": "PRINCIPAL",
          "GL Balance": 80000,
          "IHub Balance": 90000,
          "Balance Difference": -10000,
          "Match Status": "Break",
          "Anomaly Explanation": "Pattern deviation detected",            
          "Confirmed Anomaly": "Pending Review",
          "Action":""
        },
        {
          "As of Date": "30-08-2024",
          "Company": 0,
          "Account": 1619288,
          "AU": 5701,
         "Currency": "USD",
         "Primary Account": "ALL OTHER LOANS",
         "Secondary Account": "DEFERRED ORIGINATION FEES",          
         "GL Balance": 100000,
         "IHub Balance": 10000,
         "Balance Difference": 90000,
         "Match Status": "Break",
          "Anomaly Explanation": "Pattern deviation detected",          
          "Confirmed Anomaly": "Pending Review",
          "Action":""
        },
        {
          "As of Date": "30-08-2024",
          "Company": 2,
          "Account": 1619205,
          "AU": 4929,
         "Currency": "EUR",
         "Primary Account": "ALL OTHER LOANS",
          "Secondary Account": "PRINCIPAL",
          "GL Balance": 70000,
          "IHub Balance": 80000,
          "Balance Difference": -10000,
          "Match Status": "Break",
          "Anomaly Explanation": "Pattern deviation detected",          
          "Confirmed Anomaly": "Pending Review",          
          "Action":""
        }
      ]
      

      this.isLoading = false;
    } else {
      this.openDialog('Alert','Please select both files before starting reconciliation.');
    }
  }

  onReset(): void {
    this.file1 = null;
    this.file2 = null;
    this.displayData = [];
    const file1Input = document.getElementById('file1') as HTMLInputElement;
    const file2Input = document.getElementById('file2') as HTMLInputElement;
    if (file1Input) file1Input.value = '';
    if (file2Input) file2Input.value = '';
  }

  openDialog(title:string, message: string): void {
    const dialogRef = this.dialog.open(AlertDialogComponent);
    dialogRef.componentInstance.showMessage(title, message);
  }

}

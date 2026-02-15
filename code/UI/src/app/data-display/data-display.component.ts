import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, } from '@angular/common/http';
import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { AlertDialogComponent } from '../alert-dialog/alert-dialog.component';
import { RouterOutlet } from '@angular/router';



@Component({
  selector: 'app-data-display',
  imports: [CommonModule,HttpClientModule,MatTableModule,MatPaginatorModule,MatDialogModule],
  templateUrl: './data-display.component.html',
  styleUrl: './data-display.component.scss'
})
export class DataDisplayComponent implements OnInit{
  @Input() displayData: any=[];
  displayedColumns: string[] = [];
  dataSource!: MatTableDataSource<any>;

  @ViewChild(MatPaginator)
  paginator: MatPaginator = new MatPaginator;

  constructor(private dialog: MatDialog) {}
  
  ngOnInit(): void {
    if (this.displayData.length > 0) {
      this.displayedColumns = Object.keys(this.displayData[0]);   
      this.dataSource = new MatTableDataSource(this.displayData);
      this.dataSource.paginator = this.paginator;
    }
  }

  onFalsePositive(item: any): void {
    this.openDialog('Action','Raising False positive ticket for account : ' + item.Account);
  }

  onServiceNow(item: any): void {
    this.openDialog('Action','Raising Service Now ticket for  account : ' + item.Account);
  }

  onJira(item: any): void {
    this.openDialog('Action','Raising JIRA ticket for account : ' + item.Account);
  }

  onEmail(item: any): void {
    this.openDialog('Action','sending Email notification for account : ' + item.Account);
  }

  onUserComments(item: any): void {
    this.openDialog('Action','User Comments action will be added for the account : ' + item.Account);
  }

  openDialog(title:string, message: string): void {
    const dialogRef = this.dialog.open(AlertDialogComponent);
    dialogRef.componentInstance.showMessage(title, message);
  }
  
}

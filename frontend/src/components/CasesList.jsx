import React, { useState } from 'react';
import { Box, Typography, Card, CardContent, Button } from '@mui/material';

export default function CasesList({ onSelectCase }) {
  const [cases] = useState([
    {id:1, patient:'John Doe', date:'2024-12-01', status:'Reviewed'},
    {id:2, patient:'Jane Smith', date:'2024-12-02', status:'Pending'},
  ]);

  return (
    <Box>
      <Typography variant="h5" mb={2}>Cases Review</Typography>
      {cases.map(c => (
        <Card key={c.id} sx={{mb:2}}>
          <CardContent>
            <Typography variant="h6">{c.patient}</Typography>
            <Typography variant="body2">Date: {c.date}</Typography>
            <Typography variant="body2">Status: {c.status}</Typography>
            <Button variant="contained" color="primary" sx={{mt:1}} onClick={()=>onSelectCase(c)}>
              Review
            </Button>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}
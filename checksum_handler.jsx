import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const SaveChecksumHandler = () => {
  const [originalChecksum, setOriginalChecksum] = useState(null);
  const [calculatedChecksum, setCalculatedChecksum] = useState(null);
  const [isValid, setIsValid] = useState(null);

    // Calculate checksum for the save file
    const calculateChecksum = async (data) => {
        // Initialize with specific seed
        let checksum = 0x14D;
        
        // Process all bytes except checksum bytes
        for (let i = 0; i < data.length; i++) {
            if (i < 8 || i >= 12) {
                // Rotate right by 1
                checksum = ((checksum >>> 1) | (checksum << 31)) >>> 0;
                // Add byte value
                checksum = (checksum + data[i]) >>> 0;
            }
        }
        
        return checksum;
    };

  // Verify save file checksum
  const verifyChecksum = async (saveData) => {
    try {
      // Extract original checksum from header (bytes 8-11)
      const view = new DataView(saveData.buffer);
      const originalSum = view.getUint32(8, true); // Little-endian
      setOriginalChecksum(originalSum);

      // Calculate checksum of file data
      const calculatedSum = await calculateChecksum(new Uint8Array(saveData));
      setCalculatedChecksum(calculatedSum);

      // Compare checksums
      setIsValid(originalSum === calculatedSum);

      return originalSum === calculatedSum;
    } catch (err) {
      console.error('Checksum verification failed:', err);
      return false;
    }
  };

  // Update checksum in save file
  const updateChecksum = async (saveData) => {
    try {
      // Calculate new checksum
      const newChecksum = await calculateChecksum(new Uint8Array(saveData));

      // Create copy of save data
      const updatedData = new Uint8Array(saveData);
      
      // Update checksum in header (bytes 8-11)
      const view = new DataView(updatedData.buffer);
      view.setUint32(8, newChecksum, true); // Little-endian

      return updatedData;
    } catch (err) {
      console.error('Failed to update checksum:', err);
      throw err;
    }
  };

  return (
    <Card className="w-full max-w-xl">
      <CardHeader>
        <h2 className="text-xl font-bold">Save File Checksum</h2>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {originalChecksum !== null && (
            <div>
              <p>Original Checksum: {originalChecksum.toString(16)}</p>
              <p>Calculated Checksum: {calculatedChecksum.toString(16)}</p>
              <p>Status: {isValid ? "Valid" : "Invalid"}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Export both the component and the helper functions
export default SaveChecksumHandler;
export const saveHelpers = {
  calculateChecksum: calculateChecksum,
  verifyChecksum: verifyChecksum, 
  updateChecksum: updateChecksum
};
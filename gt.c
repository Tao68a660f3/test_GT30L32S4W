
void _rd_zk_data(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined1 local_18;
  undefined1 uStack_17;
  undefined1 uStack_16;
  undefined1 uStack_15;
  
  _local_18 = CONCAT13((char)param_1,
                       CONCAT12((char)((uint)param_1 >> 8),CONCAT11((char)((uint)param_1 >> 0x10),3)
                               ));
  gt_read_data(&local_18,4,param_3,param_2);
  return;
}


undefined4 ASCII_GetData(uint param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  
  if (GT_UID_MD5_FLAG < 1) {
    uVar1 = 0;
  }
  else if ((param_1 < 0x20) || (0x7e < param_1)) {
    uVar1 = 0;
  }
  else {
    switch(param_2) {
    default:
      return 0;
    case 1:
      _rd_zk_data((param_1 - 0x20) * 8 + 0x1ddf80,8,param_3);
      break;
    case 2:
      _rd_zk_data((param_1 - 0x20) * 8 + 0x1de280,8,param_3);
      break;
    case 3:
      _rd_zk_data((param_1 - 0x20) * 0xc + 0x1dbe00,0xc,param_3);
      break;
    case 4:
      _rd_zk_data((param_1 - 0x20) * 0x10 + 0x1dd780,0x10,param_3);
      break;
    case 5:
      _rd_zk_data((param_1 - 0x20) * 0x30 + 0x1dff00,0x30,param_3);
      break;
    case 6:
      _rd_zk_data((param_1 - 0x20) * 0x40 + 0x1e5a50,0x40,param_3);
      break;
    case 7:
      _rd_zk_data((param_1 - 0x20) * 0x1a + 0x1dc402,0x18,param_3);
      break;
    case 8:
      _rd_zk_data((param_1 - 0x20) * 0x1a + 0x1dcdc2,0x18,param_3);
      break;
    case 9:
      _rd_zk_data((param_1 - 0x20) * 0x22 + 0x1de582,0x20,param_3);
      break;
    case 10:
      _rd_zk_data((param_1 - 0x20) * 0x22 + 0x1df242,0x20,param_3);
      break;
    case 0xb:
      _rd_zk_data((param_1 - 0x20) * 0x4a + 0x1e22d2,0x48,param_3);
      break;
    case 0xc:
      _rd_zk_data((param_1 - 0x20) * 0x4a + 0x1e3e92,0x48,param_3);
      break;
    case 0xd:
      _rd_zk_data((param_1 - 0x20) * 0x82 + 0x1e99d2,0x80,param_3);
      break;
    case 0xe:
      _rd_zk_data((param_1 - 0x20) * 0x82 + 0x1eca92,0x80,param_3);
    }
    uVar1 = 1;
  }
  return uVar1;
}


void GB_EXT_1224(uint param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < GT_UID_MD5_FLAG) {
    if ((param_1 < 0xaaa1) || (0xaafe < param_1)) {
      if ((0xaba0 < param_1) && (param_1 < 0xabc1)) {
        iVar1 = (param_1 - 0xab42) * 0x30 + 0x1dff30;
      }
    }
    else {
      iVar1 = (param_1 - 0xaaa1) * 0x30 + 0x1dff30;
    }
    _rd_zk_data(iVar1,0x30,param_2);
  }
  return;
}


void GB_EXT_1632(uint param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < GT_UID_MD5_FLAG) {
    if ((param_1 < 0xaaa1) || (0xaafe < param_1)) {
      if ((0xaba0 < param_1) && (param_1 < 0xabc1)) {
        iVar1 = (param_1 - 0xab42) * 0x40 + 0x1e5a90;
      }
    }
    else {
      iVar1 = (param_1 - 0xaaa1) * 0x40 + 0x1e5a90;
    }
    _rd_zk_data(iVar1,0x40,param_2);
  }
  return;
}


void GB_EXT_612(uint param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < GT_UID_MD5_FLAG) {
    if ((param_1 < 0xaaa1) || (0xaafe < param_1)) {
      if ((0xaba0 < param_1) && (param_1 < 0xabc1)) {
        iVar1 = (param_1 - 0xab42) * 0xc + 0x1dbe0c;
      }
    }
    else {
      iVar1 = (param_1 - 0xaaa1) * 0xc + 0x1dbe0c;
    }
    _rd_zk_data(iVar1,0xc,param_2);
  }
  return;
}


void GB_EXT_816(uint param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < GT_UID_MD5_FLAG) {
    if ((param_1 < 0xaaa1) || (0xaafe < param_1)) {
      if ((0xaba0 < param_1) && (param_1 < 0xabc1)) {
        iVar1 = (param_1 - 0xab42) * 0x10 + 0x1dd790;
      }
    }
    else {
      iVar1 = (param_1 - 0xaaa1) * 0x10 + 0x1dd790;
    }
    _rd_zk_data(iVar1,0x10,param_2);
  }
  return;
}


void GB_SPEC_816(uint param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < GT_UID_MD5_FLAG) {
    if ((0xaca0 < param_1) && (param_1 < 0xace0)) {
      iVar1 = (param_1 - 0xaca1) * 0x10 + 0x1f2880;
    }
    _rd_zk_data(iVar1,0x10,param_2);
  }
  return;
}


void gt_12_GetData(uint param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < GT_UID_MD5_FLAG) {
    if (((param_1 < 0xa1) || (0xa9 < param_1)) || (param_2 < 0xa1)) {
      if (((0xaf < param_1) && (param_1 < 0xf8)) && (0xa0 < param_2)) {
        iVar1 = (param_2 + (param_1 - 0xb0) * 0x5e + 0x2ad) * 0x18;
      }
    }
    else {
      iVar1 = ((param_2 - 0xa1) + (param_1 - 0xa1) * 0x5e) * 0x18;
    }
    _rd_zk_data(iVar1,0x18,param_3);
  }
  return;
}


void gt_16_GetData(uint param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < GT_UID_MD5_FLAG) {
    if (((param_1 < 0xa1) || (0xa9 < param_1)) || (param_2 < 0xa1)) {
      if (((0xaf < param_1) && (param_1 < 0xf8)) && (0xa0 < param_2)) {
        iVar1 = (param_2 + (param_1 - 0xb0) * 0x5e + 0x2ad) * 0x20 + 0x2c9d0;
      }
    }
    else {
      iVar1 = ((param_2 - 0xa1) + (param_1 - 0xa1) * 0x5e) * 0x20 + 0x2c9d0;
    }
    _rd_zk_data(iVar1,0x20,param_3);
  }
  return;
}


void gt_24_GetData(uint param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < GT_UID_MD5_FLAG) {
    if (((param_1 < 0xa1) || (0xa9 < param_1)) || (param_2 < 0xa1)) {
      if (((0xaf < param_1) && (param_1 < 0xf8)) && (0xa0 < param_2)) {
        iVar1 = (param_2 + (param_1 - 0xb0) * 0x5e + 0x2ad) * 0x48 + 0x68190;
      }
    }
    else {
      iVar1 = ((param_2 - 0xa1) + (param_1 - 0xa1) * 0x5e) * 0x48 + 0x68190;
    }
    _rd_zk_data(iVar1,0x48,param_3);
  }
  return;
}


void gt_32_GetData(uint param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < GT_UID_MD5_FLAG) {
    if (((param_1 < 0xa1) || (0xa9 < param_1)) || (param_2 < 0xa1)) {
      if (((0xaf < param_1) && (param_1 < 0xf8)) && (0xa0 < param_2)) {
        iVar1 = (param_2 + (param_1 - 0xb0) * 0x5e + 0x2ad) * 0x80 + 0xedf00;
      }
    }
    else {
      iVar1 = ((param_2 - 0xa1) + (param_1 - 0xa1) * 0x5e) * 0x80 + 0xedf00;
    }
    _rd_zk_data(iVar1,0x80,param_3);
  }
  return;
}


"""
Different categories of data and their settings to be generated
"""

import json
import os

from device_checker import get_write_path

_POSTFIX_WMIC = "/format:list"
_POSTFIX_PATH = 'get /value'

CATEGORIES = {
    'services': {
        "name": "Services",
        "title": "{} - {}",
        "title_keys": ['Name', 'DisplayName'],
        "command": "wmic service get",
        'command_postfix': _POSTFIX_WMIC,
        "hash_key": "Name",
        'file': 'services.json',
        "compare_keys": [
            'DelayedAutoStart',
            "Caption",
            "CheckPoint",
            "DesktopInteract",
            "DisplayName",
            "ErrorControl",
            "PathName",
            "ServiceType",
            "StartMode",
            "StartName",
        ],
    },
    'startup': {
        "name": "Startup Programs",
        "title": "{} - {}",
        "title_keys": ['Name', 'Command'],
        "command": "wmic startup get",
        'command_postfix': _POSTFIX_WMIC,
        "hash_key": "Name",
        'file': 'startup.json',
        "compare_keys": [
            'Caption',
            'Command',
            'Description',
            'Location',
            'User',
            'UserSID',
        ],
    },
    'installed_programs': {
        "name": "Installed Programs",
        "title": "{} - v{}",
        "title_keys": ['Name', 'Version'],
        "command": "wmic product get",
        'command_postfix': _POSTFIX_WMIC,
        "hash_key": "IdentifyingNumber",
        'file': 'installed.json',
        "compare_keys": [
            'Caption',
            'Description',
            'HelpLink',
            'HelpTelephone',
            'IdentifyingNumber',
            'InstallDate',
            'InstallDate2',
            'InstallLocation',
            'InstallSource',
            'InstallState',
            'Name',
            'LocalPackage',
            'PackageCache',
            'PackageCode',
            'PackageName',
            'ProductID',
            'RegCompany',
            'RegOwner',
            'SKUNumber',
            'URLInfoAbout',
            'URLUpdateInfo',
            'Vendor',
            'Version'
        ],
    },
    'usb': {
        "name": "USB Controllers",
        "title": "{} - {}",
        "title_keys": ['Name', 'Manufacturer'],
        "command": "wmic path CIM_USBController",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "DeviceID",
        'file': 'usb.json',
        "compare_keys": [
            'Availability',
            'Caption',
            'Description',
            'InstallDate',
            'Manufacturer',
            'Name',
            'PNPDeviceID',
            'Status',
            'SystemName',
        ],
    },
    'physical_disks': {
        "name": "Physical Disks",
        "title": "{} - {} - {}",
        "title_keys": ['Model', 'Name', 'SerialNumber'],
        "command": "wmic path CIM_DiskDrive",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "PNPDeviceID",
        'file': 'disks.json',
        "compare_keys": [
            'Availability',
            'BytesPerSector',
            'Caption',
            'Description',
            'DeviceID',
            'FirmwareRevision',
            'Index',
            'InstallDate',
            'InterfaceType',
            'Manufacturer',
            'MediaLoaded',
            'MediaType',
            'Model',
            'Name',
            'NeedsCleaning',
            'Partitions',
            'SCSIBus',
            'SCSILogicalUnit',
            'SCSIPort',
            'SCSITargetId',
            'SectorsPerTrack',
            'SerialNumber',
            'Size',
            'Status',
            'SystemName',
            'TotalCylinders',
            'TotalHeads',
            'TotalSectors',
            'TotalTracks',
            'TracksPerCylinder',
        ],
    },
    'logical_disks': {
        "name": "Logical Disks",
        "title": "{}",
        "title_keys": ['Name'],
        "command": "wmic path CIM_LogicalDisk",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "Name",
        "file": 'logical.json',
        "compare_keys": [
            'Availability',
            'Caption',
            'Description',
            'DeviceID',
            'InstallDate',
            'MediaType',
            'Status',
            'StatusInfo',
            'SystemName',
        ]
    },
    'ide': {
        "name": "IDE Devices",
        "title": "{}",
        "title_keys": ['Name'],
        "command": "wmic path Win32_IDEController",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "PNPDeviceID",
        "file": 'ide.json',
        "compare_keys": [
            'Availability',
            'Caption',
            'Description',
            'DeviceID',
            'InstallDate',
            'Manufacturer',
            'Name',
            'Status',
            'StatusInfo',
        ]
    },
    'scsi': {
        "name": "SCSI Devices",
        "title": "{}",
        "title_keys": ['Name'],
        "command": "wmic path CIM_SCSIController",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "PNPDeviceID",
        "file": 'scsi.json',
        "compare_keys": [
            'Availability',
            'Caption',
            'Description',
            'DeviceID',
            'InstallDate',
            'Name',
            'Status',
            'StatusInfo',
        ]
    },
    'env': {
        "name": "Environment Variables",
        "title": "{} - {}",
        "title_keys": ['Name', 'UserName'],
        "command": "wmic path Win32_Environment",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": ["Name", "SystemVariable", "UserName"],
        'file': 'environment.json',
        "compare_keys": [
            'Caption',
            'Description',
            'InstallDate',
            'Status',
            'VariableValue',
        ],
    },
    'printers': {
        "name": "Printers",
        "title": "{}",
        "title_keys": ['Name'],
        "command": "wmic path CIM_Printer",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "DeviceID",
        'file': 'printers.json',
        "compare_keys": [
            'Attributes',
            'Capabilities',
            'CapabilityDescriptions',
            'Caption',
            'Default',
            'Direct',
            'DriverName',
            'ExtendedPrinterStatus',
            'Hidden',
            'Local',
            'Name',
            'Network',
            'PNPDeviceID',
            'PortName',
            'PrinterPaperNames',
            'Priority',
            'SpoolEnabled',
            'SystemName',
        ],
    },
    'cdrom': {
        "name": "CDROMs",
        "title": "{}",
        "title_keys": ['Name'],
        "command": "wmic path CIM_CDROMDrive",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "DeviceID",
        'file': 'cdrom.json',
        "compare_keys": [
            'Caption',
            'Description',
            'InstallDate',
            'Status',
            'Availability',
            'PowerManagementCapabilities',
            'StatusInfo',
            'SystemName',
            'Capabilities',
            'MaxBlockSize',
            'MaxMediaSize',
            'MinBlockSize',
            'NeedsCleaning',
            'NumberOfMediaSupported',
        ],
    },
    'network': {
        "name": "Network Adapters",
        "title": "{}",
        "title_keys": ['Name'],
        "command": "wmic path CIM_NetworkAdapter",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "DeviceID",
        'file': 'network.json',
        "compare_keys": [
            'AdapterType',
            'AdapterTypeId',
            'AutoSense',
            'Availability',
            'Caption',
            'ConfigManagerUserConfig',
            'Description',
            'GUID',
            'Index',
            'Installed',
            'MACAddress',
            'Manufacturer',
            'Name',
            'PhysicalAdapter',
            'PowerManagementSupported',
            'ServiceName',
            'SystemName',
        ],
    },
    'pointing': {
        "name": "Pointing Devices",
        "title": "{} - {}",
        "title_keys": ['Name', 'Manufacturer'],
        "command": "wmic path Win32_PointingDevice",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "DeviceID",
        'file': 'pointing.json',
        "compare_keys": [
            'Availability',
            'Caption',
            'ConfigManagerUserConfig',
            'Description',
            'DeviceInterface',
            'HardwareType',
            'InfFileName',
            'InfSection',
            'Manufacturer',
            'Name',
            'NumberOfButtons',
            'PNPDeviceID',
            'PointingType',
            'Status',
            'StatusInfo',
            'SystemName',
        ],
    },
    'keyboards': {
        "name": "Keyboards",
        "title": "{} - {}",
        "title_keys": ['Description', 'DeviceID'],
        "command": "wmic path Win32_Keyboard",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "DeviceID",
        'file': 'keyboards.json',
        "compare_keys": [
            'Availability',
            'Caption',
            'ConfigManagerUserConfig',
            'Description',
            'IsLocked',
            'Layout',
            'Name',
            'Status',
            'StatusInfo',
            'SystemName',
        ],
    },
    'displays': {
        "name": "Displays",
        "title": "{}",
        "title_keys": ['Name'],
        "command": "wmic path CIM_Display",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "DeviceID",
        'file': 'displays.json',
        "compare_keys": [
            'Availability',
            'Caption',
            'ConfigManagerUserConfig',
            'Description',
            'DisplayType',
            'IsLocked',
            'Name',
            'PNPDeviceID',
            'MonitorManufacturer',
            'MonitorType',
            'Status',
            'StatusInfo',
            'SystemName',
        ],
    },
    'video': {
        "name": "Video Controllers",
        "title": "{}",
        "title_keys": ['Name'],
        "command": "wmic path CIM_VideoController",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "DeviceID",
        'file': 'video.json',
        "compare_keys": [
            'Availability',
            'AdapterCompatibility',
            'AdapterDACType',
            'AdapterRAM',
            'Caption',
            'ConfigManagerUserConfig',
            'CurrentBitsPerPixel',
            'CurrentHorizontalResolution',
            'CurrentNumberOfColors',
            'CurrentNumberOfColumns',
            'CurrentNumberOfRows',
            'CurrentRefreshRate',
            'CurrentScanMode',
            'CurrentVerticalResolution',
            'Description',
            'InfFilename',
            'InfSection',
            'InstalledDisplayDrivers',
            'MaxRefreshRate',
            'MinRefreshRate',
            'Monochrome',
            'Name',
            'PNPDeviceID',
            'Status',
            'StatusInfo',
            'VideoArchitecture',
            'VideoMemoryType',
            'VideoMode',
            'VideoModeDescription',
            'VideoProcessor',
        ],
    },
    'sound': {
        "name": "Sound Devices",
        "title": "{}",
        "title_keys": ['Name'],
        "command": "wmic path Win32_SoundDevice",
        'command_postfix': _POSTFIX_PATH,
        "hash_key": "DeviceID",
        'file': 'sound.json',
        "compare_keys": [
            'Availability',
            'Caption',
            'ConfigManagerUserConfig',
            'Description',
            'Manufacturer',
            'MPU401Address',
            'PNPDeviceID',
            'ProductName',
            'Status',
            'StatusInfo',
            'SystemName',
        ],
    },
    'users': {
        "name": "Users",
        "title": "{} - {}",
        "title_keys": ['Name', 'Caption'],
        "command": "wmic USERACCOUNT get",
        'command_postfix': _POSTFIX_WMIC,
        "hash_key": "Caption",
        'file': 'users.json',
        "compare_keys": [
            'AccountType',
            'Description',
            'Disabled',
            'Domain',
            'FullName',
            'InstallDate',
            'LocalAccount',
            'Lockout',
            'Name',
            'PasswordChangeable',
            'PasswordExpires',
            'PasswordRequired',
            'SID',
            'SIDType',
            'Status',
        ],
    },
    'groups': {
        "name": "Groups",
        "title": "{} - {}",
        "title_keys": ['Name', 'Caption'],
        "command": "wmic GROUP get",
        'command_postfix': _POSTFIX_WMIC,
        "hash_key": "Caption",
        'file': 'groups.json',
        "compare_keys": [
            'Description',
            'Domain',
            'InstallDate',
            'LocalAccount',
            'Name',
            'SID',
            'SIDType',
            'Status',
        ],
    },
}


def load_categories():
    """
    Load difference data for categories
    """

    for _, value in CATEGORIES.items():
        file_name = "diff_{}".format(value['file'])

        path = get_write_path(file_name)
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                value['diff'] = json.load(f)
        else:
            value['diff'] = None


load_categories()

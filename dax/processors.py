""" Processor class define for Scan and Session """
import os
import re
import task
import logging
import XnatUtils
import yaml

#Logger for logs
LOGGER = logging.getLogger('dax')

class Processor(object):
    """ Base class for processor """
    def __init__(self, walltime_str, memreq_mb, spider_path,
                 version=None, ppn=1, suffix_proc='',
                 xsitype='proc:genProcData'):
        """
        Entry point of the Base class for processor.

        :param walltime_str: Amount of walltime to request for the process
        :param memreq_mb: Number of megabytes of memory to use
        :param spider_path: Fully qualified path to the spider to run
        :param version: Version of the spider
        :param ppn: Number of processors per not to use.
        :param suffix_proc: Processor suffix (if desired)
        :param xsitype: the XNAT xsiType.
        :return: None

        """
        self.walltime_str = walltime_str # 00:00:00 format
        self.memreq_mb = memreq_mb  # memory required in megabytes
        #default values:
        self.version = "1.0.0"
        if not suffix_proc:
            self.suffix_proc = ''
        else:
            if suffix_proc and suffix_proc[0] != '_':
                self.suffix_proc = '_'+suffix_proc
            else:
                self.suffix_proc = suffix_proc

        self.suffix_proc = self.suffix_proc.strip().replace(" ","")\
                               .replace('/','_').replace('*','_')\
                               .replace('.','_').replace(',','_')\
                               .replace('?','_').replace('!','_')\
                               .replace(';','_').replace(':','_')
        self.name = None
        self.spider_path = spider_path
        self.ppn = ppn
        self.xsitype = xsitype
        #getting name and version from spider_path
        self.set_spider_settings(spider_path, version)
        #if suffix_proc is empty, set it to "" for the spider call:
        if not suffix_proc:
            self.suffix_proc = ''

    #get the spider_path right with the version:
    def set_spider_settings(self, spider_path, version):
        """
        Method to set the spider version, path, and name from filepath

        :param spider_path: Fully qualified path and file of the spider
        :param version: version of the spider
        :return: None

        """
        if version:
            #get the proc_name
            proc_name = os.path.basename(spider_path)[7:-3]
            #remove any version if there is one
            proc_name = re.split("/*_v[0-9]/*", proc_name)[0]
            #setting the version and name of the spider
            self.version = version
            self.name = '''{procname}_v{version}{suffix}'''.format(procname=proc_name,
                                                                   version=self.version.split('.')[0],
                                                                   suffix=self.suffix_proc)
            spider_name = '''Spider_{procname}_v{version}.py'''.format(procname=proc_name,
                                                                      version=version.replace('.', '_'))
            self.spider_path = os.path.join(os.path.dirname(spider_path), spider_name)
        else:
            self.default_settings_spider(spider_path)

    def default_settings_spider(self, spider_path):
        """
        Get the default spider version and name

        :param spider_path: Fully qualified path and file of the spider
        :return: None

        """
        #set spider path
        self.spider_path = spider_path
        #set the name and the version of the spider
        if len(re.split("/*_v[0-9]/*", spider_path)) > 1:
            self.version = os.path.basename(spider_path)[7:-3].split('_v')[-1].replace('_','.')
            spidername = os.path.basename(spider_path)[7:-3]
            self.name = '''{procname}_v{version}{suffix}'''.format(procname=re.split("/*_v[0-9]/*", spidername)[0],
                                                                   version=self.version.split('.')[0],
                                                                   suffix=self.suffix_proc)
        else:
            self.name = os.path.basename(spider_path)[7:-3]+self.suffix_proc

    # has_inputs - does this object have the required inputs?
    # e.g. NIFTI format of the required scan type and quality and are there no conflicting inputs.
    # i.e. only 1 required by 2 found?
    # other arguments here, could be Proj/Subj/Sess/Scan/Assessor depending on processor type?
    def has_inputs(self):
        """
        Check to see if the spider has all the inputs necessary to run.

        :raises: NotImplementedError if user does not override
        :return: None

        """
        raise NotImplementedError()

    # should_run - is the object of the proper object type?
    # e.g. is it a scan? and is it the required scan type?
    # e.g. is it a T1?
    # other arguments here, could be Proj/Subj/Sess/Scan/Assessor depending on processor type?
    def should_run(self):
        """
        Responsible for determining if the assessor should shouw up in the XNAT Session.

        :raises: NotImplementedError if not overridden.
        :return: None

        """
        raise NotImplementedError()

    def build_cmds(self, cobj, dir):

        """
        Build the commands that will go in the PBS/SLURM script
        :raises: NotImplementedError if not overridden from base class.
        :return: None
        """
        raise NotImplementedError()

class ScanProcessor(Processor):
    """ Scan Processor class for processor on a scan on XNAT """
    def __init__(self, scan_types, walltime_str, memreq_mb, spider_path, version=None, ppn=1, suffix_proc=''):
        """
        Entry point of the ScanProcessor Class.

        :param scan_types: Types of scans that the spider should run on
        :param walltime_str: Amount of walltime to request for the process
        :param memreq_mb: Amount of memory in megavytes to request for the process
        :param spider_path: Absolute path to the spider
        :param version: Version of the spider (taken from the file name)
        :param ppn: Number of processors per node to request
        :param suffix_proc: Processor suffix
        :return: None

        """
        super(ScanProcessor, self).__init__(walltime_str, memreq_mb, spider_path, version, ppn, suffix_proc)
        if isinstance(scan_types, list):
            self.scan_types = scan_types
        elif isinstance(scan_types, str):
            if scan_types == 'all':
                self.scan_types = 'all'
            else:
                self.scan_types = scan_types.split(',')
        else:
            self.scan_types = []

    def has_inputs(self):
        """
        Method to check and see that the process has all of the inputs that it needs to run.

        :raises: NotImplementedError if not overridden.
        :return: None

        """
        raise NotImplementedError()

    def get_assessor_name(self, cscan):
        """
        Returns the label of the assessor

        :param cscan: CachedImageScan object from XnatUtils
        :return: String of the assessor label

        """
        scan_dict = cscan.info()
        subj_label = scan_dict['subject_label']
        sess_label = scan_dict['session_label']
        proj_label = scan_dict['project_label']
        scan_label = scan_dict['scan_label']
        return proj_label+'-x-'+subj_label+'-x-'+sess_label+'-x-'+scan_label+'-x-'+self.name

    def get_task(self, intf, cscan, upload_dir):
        """
        Get the Task object

        :param intf: XNAT interface (pyxnat.Interface class)
        :param cscan: CachedImageScan object from XnatUtils
        :param upload_dir: the directory to put the processed data when the
         process is done
        :return: Task object

        """
        scan_dict = cscan.info()
        assessor_name = self.get_assessor_name(cscan)
        scan = XnatUtils.get_full_object(intf, scan_dict)
        assessor = scan.parent().assessor(assessor_name)
        return task.Task(self, assessor, upload_dir)

    def should_run(self, scan_dict):
        """
        Method to see if the assessor should appear in the session.

        :param scan_dict: Dictionary of information about the scan
        :return: True if it should run, false if it shouldn't

        """
        if self.scan_types == 'all':
            return True
        else:
            return scan_dict['scan_type'] in self.scan_types

class MultiScanProcessorYAML(Processor):
    """ Base class for scan processors built with YAML"""
    def __init__(self, yaml_dict, walltime_str=None, scan_types=None, memreq_mb=None, spider_path=None, version=None, suffix_proc=None, ppn=None, file_paths=None, assessor_types=None, name="generic_multi_scan_processor"):
        super(MultiScanProcessorYAML, self).__init__(walltime_str if walltime_str else yaml_dict["walltime_str"],
                                                memreq_mb if memreq_mb else yaml_dict["memreq_mb"],
                                                spider_path if spider_path else yaml_dict["spider_path"],
                                                version if version else yaml_dict["version"],
                                                ppn if ppn else yaml_dict.get("ppn",1),
                                                suffix_proc if suffix_proc else '')
        self.yaml = yaml_dict
        self.name = yaml_dict["name"]
        self.version = yaml_dict.get("version","")
        if not self.version.startswith("v"):
            self.version = "v"+self.version
        self.scan_dict = yaml_dict.get("scans", {})
        self.assessor_dict = yaml_dict.get("assessors", {})
        self.files_dict = yaml_dict.get("local_files", {})
        # to be consistent
        self.scan_keys = self.scan_dict.keys()
        self.cmd = yaml_dict["command"]
        self.spider_path = yaml_dict["spider_path"]
        self.assessor_keys = self.assessor_dict.keys()
        self.required_assessor_keys = []
        self.nonrequired_assessor_keys = []
        self.build_required_assessor_keys()
        self.file_keys = self.files_dict.keys()

        self.reference_dict = {}

        self.name = yaml_dict.get("name", name)

        # Allow for non-default scan, file, and assessors
        if scan_types:
            self.__parse_scan_types(scan_types)
        if file_paths:
            self.__parse_file_paths(file_paths)
        if assessor_types:
            self.__parse_assessor_types(assessor_types)

    def get_cmds(self, assessor, tmp_dir):
        reference_dict = {}
        project = assessor.parent().parent().parent().label()
        subject = assessor.parent().parent().label()
        session = assessor.parent().label()
        reference_dict["project"] = project
        reference_dict["subject"] = subject
        reference_dict["session"] = session
        reference_dict["tmpdir"] = tmp_dir
        reference_dict["spider_path"] = self.spider_path

        xnat = XnatUtils.get_interface()
        csess = XnatUtils.CachedImageSession(xnat, project, subject, session)

        cached_assessors = csess.assessors()
        assessor_name_dict = {x.info()["ID"]:x.info()["label"] for x in cached_assessors}

        assessor_name = assessor.label()
        assessor_info = assessor_name.split('-x-')[3]
        scans = filter(lambda x: x, assessor_info.split("-x1x-")[0].split("-a-"))
        assrs = filter(lambda x: x, assessor_info.split("-x1x-")[1].split("-x2x-")[0].split("-b-"))
        d_assrs = filter(lambda x: x, assessor_info.split("-x2x-")[1].split("-c-"))

        for i in xrange(len(scans)):
            reference_dict[self.scan_keys[i]] = scans[i]
        for i in xrange(len(assrs)):
            assr_label = assessor_name_dict[assrs[i]]
            reference_dict[self.required_assessor_keys[i][0]] = assr_label
        for i in xrange(len(d_assrs)):
            assr_label = assessor_name_dict[d_assrs[i]]
            reference_dict[self.nonrequired_assessor_keys[i][0]] = assr_label
        for i in xrange(len(self.file_keys)):
            reference_dict[self.file_keys[i]] = self.files_dict[self.file_keys[i]]

        cmd = self.cmd.format(**reference_dict)

        return [cmd]


    def get_name(self):
        return "_".join([self.name, self.version])

    def get_assessor_name(self, scan_names, ass_info, d_ass_info, csess):
        name = ""
        if len(scan_names) > 0:
            scan_name = "-a".join([x["scan_id"] for x in scan_names])
            name += scan_name
        name += "-x1x-"
        if len(ass_info) > 0:
            ass_name = "-b-".join([x["assessor_id"] for x in ass_info])
            name += ass_name
        name += "-x2x-"
        if len(d_ass_info) > 0:
            d_ass_name = "-c-".join([x["assessor_id"] for x in d_ass_info])
            name += d_ass_name

        csess_info = csess.info()
        project = csess_info["project_label"]
        session = csess_info["session_label"]
        subject = csess_info["subject_label"]
        name = "-x-".join([project, subject, session, name, self.get_name()])
        return name

    def __build_reference_dict(self, yaml_dict):
        for scan in self.scan_keys:
            reference_name = self.scan_dict[scan].get("reference_name", scan)
            self.reference_dict[reference_name] = self.scan_dict[scan]
        for assessor in self.assessor_keys:
            reference_name = self.assessor_dict[assessor].get("reference_name", assessor)
            self.reference_dict[reference_name] = self.assessor_dict[assessor]
        for file_name in self.file_keys:
            reference_name = self.files_dict[file_name].get("reference_name", file_name)
            self.reference_dict[reference_name] = self.files_dict[file_name]

        self.reference_dict["spider_path"] = yaml_dict["spider_path"]

    def build_required_assessor_keys(self):
        # helper function to determine which keys are required
        for i, assessor in enumerate(self.assessor_keys):
            # if the assessor is not derived from another scan, it is required
            if not self.assessor_dict[assessor].get("derive_from", False):
                self.required_assessor_keys.append((assessor,i))
            else:
                self.nonrequired_assessor_keys.append((assessor,i))

    def should_run(self, scan_list, ass_list, csess, casses):

        # check if any scans are in either the known good or bad lists if provided
        scan_names = [x["scan_label"] for x in scan_list]
        for i, scan in enumerate(scan_list):
            scan_YAML_info = self.scan_dict[self.scan_keys[i]]
            scan_quality = scan.get("quality", "unknown")
            quality_dict = scan_YAML_info.get("quality",{})
            in_list = quality_dict.get("in")
            out_list = quality_dict.get("out")

            if in_list and not scan_quality in set(in_list):
                out_str = "Scan %s's quality %s is not in the acceptable scan qualities (%s) for processor %s" % (scan["scan_id"], scan_quality, ",".join(in_list), self.name)
                return False, out_str
            if out_list and not scan_quality in set(in_list):
                out_str = "Scan %s's quality %s is not in the unacceptable scan qualities (%s) for processor %s" % (scan["scan_id"], scan_quality, ",".join(out_list), self.name)
                return False, out_str

        # check if any required assessors are in either the known good or bad lists if provided
        for i, ass in enumerate(ass_list):
            ass_YAML_info = self.assessor_dict[self.required_assessor_keys[i][0]]
            ass_quality = ass.get("quality", "unknown")
            quality_dict = ass_YAML_info.get("quality", {})
            in_list = quality_dict.get("in")
            out_list = quality_dict.get("out")

            if in_list and not ass_quality in set(in_list):
                out_str = "Assessor %s's quality %s is not in the acceptable assessor qualities (%s) for processor %s" % (ass["label"], ass_quality, ",".join(in_list), self.name)
                return False, out_str
            if out_list and not ass_quality in set(in_list):
                out_str = "Assessor %s's quality %s is not in the unacceptable assessor qualities (%s) for processor %s" % (ass["label"], ass_quality, ",".join(out_list), self.name)
                return False, out_str

        # check if any derived assessors are in either the known good or bad lists if provided
        ass_names = [x.label() for x in casses]
        derived_assessors = []
        for i, ass in enumerate(self.nonrequired_assessor_keys):
            ass_name = ass[0]
            ass_number = ass[1]
            ass_YAML_info = self.assessor_dict[ass_name]

            derive_from = ass_YAML_info.get("derive_from",[])
            valid_assessors = filter(lambda x: x.endswith(ass_name) , ass_names)
            for df in derive_from:
                scan_idx = filter(lambda x: self.scan_keys[x], range(len(self.scan_keys)))[0]
                scan_name = scan_list[scan_idx]["label"]
                valid_assessors = filter(lambda x: x.find(scan_name) > -1, valid_assessors)

            if len(valid_assessors) == 0:
                return False, "There were no valid assessors of type %s" % ass_name

            good_assessors = []
            for ass_i in valid_assessors:
                for j, a in enumerate(casses):
                    if ass_names[j] == ass_i:
                        ass = a
                        break
                ass = ass.info()

                ass_quality = ass.get("quality", "unknown")
                quality_dict = ass_YAML_info.get("quality", {})
                in_list = quality_dict.get("in")
                out_list = quality_dict.get("out")

                if in_list and not ass_quality in set(in_list):
                    continue
                if out_list and not ass_quality in set(in_list):
                    continue
                good_assessors.append(ass)
            if len(good_assessors) == 0:
                return False, "There were no valid assessors of type %s" % ass_name
            derived_assessors.append(good_assessors)

        return True, derived_assessors


    def get_requirements_list(self):
        scan_needs = []
        ass_needs = []
        for scan in self.scan_keys:
            scan_needs.append(self.scan_dict[scan]["types"])
        for ass in self.required_assessor_keys:
            ass_needs.append(self.assessor_dict[ass[0]]["types"])
        return scan_needs, ass_needs

    def __parse_file_paths(self, file_paths):
        for file_path in file_paths.keys():
            self.files_dict[file_path] = file_paths[file_path]

    def __parse_scan_types(self, scan_types):
        for scan_types in scan_types.keys():
            self.scan_dict[scan_type]["types"] = scan_types[scan_type]

    def __parse_assessor_types(self, assessor_types):
        for assessor_type in assessor_types.keys():
            self.assessor_dict[assessor_type]["types"] = resource_types[resource_type]


    def test(self):
        # check if all the scans specify resources
        for scan in self.scan_dict.keys():
            resources = scan_dict[scan].get("resources",[])
            if len(resources) == 0:
                print >> sys.stderr, "Error! Scan %s does not specify any resources" % scan
        for assessor in assessor_dict.keys():
            resources = assessor_dict[assessor].get("resources", [])
            if len(resources) == 0:
                print >> sys.stderr, "Error! Resource %s does not specify any resources" % assessor
            types = assessor_dict[assessor].get("types", [])
            if len(types) == 0:
                print >> sys.stderr, "Error! Resource %s does not specify any types" % assessor

    @staticmethod
    def determine_scan_assessor_groups(scan_list, ass_list, scan_reqs, ass_reqs):
        grouped_scans = []
        grouped_asses = []
        if scan_reqs:
            for scan_req in scan_reqs:
                scans = []
                for scan in scan_list:
                    scan_l = scan["scan_type"].lower()
                    for sr in scan_req:
                        sr = sr.lower()
                        if sr == scan_l:
                            scans.append(scan)
                grouped_scans.append(scans)
        if ass_reqs:
            for ass_req in ass_reqs:
                asses = []
                for ass in ass_list:
                    ass_l = ass["proctype"].lower()
                    for ar in ass_req:
                        ar = ar.lower()
                        if ar == ass_l:
                            asses.append(ass)
                grouped_asses.append(asses)
        return grouped_scans, grouped_asses



class SessionProcessor(Processor):
    """ Session Processor class for processor on a session on XNAT """
    def __init__(self, walltime_str, memreq_mb, spider_path, version=None, ppn=1, suffix_proc=''):
        """
        Entry point for the session processor

        :param walltime_str: Amount of walltime to request for the process
        :param memreq_mb: Amount of memory in megavytes to request for the process
        :param spider_path: Absolute path to the spider
        :param version: Version of the spider (taken from the file name)
        :param ppn: Number of processors per node to request
        :param suffix_proc: Processor suffix
        :return: None

        """
        super(SessionProcessor, self).__init__(walltime_str, memreq_mb, spider_path, version, ppn, suffix_proc)

    def has_inputs(self):
        """
        Check to see that the session has the required inputs to run.

        :raises: NotImplementedError if not overriden from base class.
        :return: None
        """
        raise NotImplementedError()

    def should_run(self, session_dict):
        """
        By definition, this should always run, so it just returns true with no checks

        :param session_dict: Dictionary of session information for
         XnatUtils.list_experiments()
        :return: True

        """
        return True

    def get_assessor_name(self, csess):
        """
        Get the name of the assessor

        :param csess: CachedImageSession from XnatUtils
        :return: String of the assessor label

        """
        session_dict = csess.info()
        proj_label = session_dict['project']
        subj_label = session_dict['subject_label']
        sess_label = session_dict['label']
        return proj_label+'-x-'+subj_label+'-x-'+sess_label+'-x-'+self.name

    def get_task(self, intf, csess, upload_dir):
        """
        Return the Task object

        :param intf: XNAT interface see pyxnat.Interface
        :param csess: CachedImageSession from XnatUtils
        :param upload_dir: directory to put the data after run on the node
        :return: Task object of the assessor

        """
        sess_info = csess.info()
        assessor_name = self.get_assessor_name(csess)
        session = XnatUtils.get_full_object(intf, sess_info)
        assessor = session.assessor(assessor_name)
        return task.Task(self, assessor, upload_dir)

def processors_by_type(proc_list):
    """
    Organize the processor types and return a list of session processors
     first, then scan

    :param proc_list: List of Processor classes from the DAX settings file
    :return: List of SessionProcessors, and list of ScanProcessors

    """
    sess_proc_list = list()
    scan_proc_list = list()
    multi_scan_proc_list = list()

    # Build list of processors by type
    for proc in proc_list:
        if issubclass(proc.__class__, ScanProcessor):
            scan_proc_list.append(proc)
        elif issubclass(proc.__class__, MultiScanProcessorYAML):
            multi_scan_proc_list.append(proc)
        elif issubclass(proc.__class__, SessionProcessor):
            sess_proc_list.append(proc)
        else:
            LOGGER.warn('unknown processor type:'+proc)

    return sess_proc_list, scan_proc_list, multi_scan_proc_list

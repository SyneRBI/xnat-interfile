/*
 * xnat-interfile-plugin:
 * XNAT http://www.xnat.org
 * Copyright (c) 2022, Physikalisch-Technische Bundesanstalt
 * All Rights Reserved
 *
 * Released under Apache 2.0
 */

package org.nrg.xnat.interfile;

import org.nrg.framework.annotations.XnatDataModel;
import org.nrg.framework.annotations.XnatPlugin;
import org.nrg.xdat.bean.InterfileItfscandataBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;

@XnatPlugin(value = "itfPlugin", name = "XNAT 1.8 Interfile plugin",
            dataModels = {@XnatDataModel(value = InterfileItfscandataBean.SCHEMA_ELEMENT_NAME,
                                         singular = "PET raw data",
                                         plural = "PET raw data",
                                         code = "INTERFILE")})
public class InterfileXnatPlugin {
}
